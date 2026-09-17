# Big Data Analytics with AI — News Intelligence Platform

A Django site that turns a preprocessed Central News Agency (CNA) corpus
into thirteen analytical views: keyword ranking, named-entity ranking,
person ranking, trending content, full-text search, per-keyword sentiment,
keyword association, correlation between keyword pairs, Netflix / streaming
mention analysis, and BERT-powered live sentiment + content-based news
recommendation.

> **Academic context:** capstone deliverable for a graduate Big Data /
> Business Intelligence course. It builds on the earlier midterm
> project (`Big-data-analytics`, 5 apps) by adding user-driven keyword
> analytics, correlation, streaming-service comparisons, and two
> BERT-backed apps (live sentiment scoring and content-based news
> recommendation).

---

## Table of Contents

- [System Architecture](#system-architecture)
- [Repository Layout](#repository-layout)
- [App Anatomy](#app-anatomy)
- [Data Flow](#data-flow)
- [Tech Stack](#tech-stack)
- [Requirements](#requirements)
- [Configuration](#configuration)
- [Running Locally](#running-locally)
- [Data Prerequisites](#data-prerequisites)
- [Deployment Notes](#deployment-notes)
- [What's Not in the Repo](#whats-not-in-the-repo)
- [License](#license)

---

## System Architecture

```
                          ┌─────────────────┐
                          │    Browser      │
                          │  (Chrome/etc.)  │
                          └────────┬────────┘
                                   │  GET (page) / POST (JSON)
                                   ▼
                          ┌─────────────────┐
                          │  Django 2.2     │
                          │ website_configs │  ← settings.py + urls.py
                          └────────┬────────┘
                                   │  path()-based dispatch
   ┌───────────────────────────────┼─────────────────────────────────────┐
   │  Read-only aggregation apps   │  User-driven query apps             │
   │                               │                                     │
   ▼                               ▼                                     ▼
 /topword/    /topner/       /userkeyword/         /correlation/    /sentiment/
 /topperson/  /topyesterday/ /userkeyword_assoc/                    /rcmd/
 /topresearch/                /userkeyword_senti/
                              /netflix/    /stream/
   │                               │                                     │
   │  pd.read_csv                  │  pd.read_csv + filter               │
   │  slice top-N                  │  (date range, category,             │
   │  → chart JSON                 │   and/or keyword logic)             │
   │                               │  → chart / cloud / line JSON        │
   │                               │                                     │
   ▼                               ▼                                     ▼
 ┌────────────────────────────────────────┐          ┌──────────────────────────┐
 │  app_top_*/dataset/*.csv               │          │  transformers +          │
 │  app_user_*/dataset/*.csv              │          │  Hugging Face model:     │
 │  app_correlation/dataset/*.csv         │          │  clhuang/albert-sentiment│
 │  app_netflix/dataset/*.csv             │          │                          │
 │  app_stream/dataset/*.csv              │          │  news_sim_martrix.npy    │
 │  app_news_rcmd_bert/dataset/*.csv,.npy │          │  (precomputed BERT sim)  │
 └────────────────────────────────────────┘          └──────────────────────────┘
                                   │
                                   ▼
                        JSON → jQuery → Chart.js / word cloud / list view
```

### Key design choices

- **13 self-contained Django apps.** Every feature is its own app with its
  own `views.py`, `urls.py`, `templates/<app>/home.html`, and
  `dataset/` folder — you can add or remove one without touching the
  others. `website_configs/urls.py` mounts each app under a short URL
  prefix.
- **Two data-loading patterns.** Small "read-only aggregate" apps load a
  CSV at module import into a dict and slice it per request
  (`app_top_*`). Larger "user-query" apps keep the full DataFrame in a
  global `df` and re-filter it per request over a date window (`app_user_*`,
  `app_correlation`, `app_news_rcmd_bert`).
- **Cross-app data sharing.** `app_user_keyword_association` and
  `app_user_keyword_sentiment` import `df` directly from
  `app_user_keyword.views` to avoid loading the same CSV twice into RAM.
- **BERT lives locally.** `app_sentiment_bert` loads
  `clhuang/albert-sentiment` from Hugging Face at start-up so live text
  can be scored. `app_news_rcmd_bert` uses a precomputed
  `news_sim_martrix.npy` similarity matrix — recommendations are just
  matrix lookups at request time, no model call.

---

## Repository Layout

```
Big-data-analytics-with-AI/
├── manage.py
├── db.sqlite3                             # Django auth tables only
├── db_1.sqlite3                           # earlier snapshot
├── templates/
│   └── navbar.html                        # shared cross-app top nav
├── website_configs/
│   ├── settings.py                        # 13 apps registered + CORS
│   ├── urls.py                            # 13 path() entries
│   └── wsgi.py
│
├── app_top_keyword/            # /topword/          — top keywords per category
├── app_top_person/             # /topperson/        — top mentioned people
├── app_top_ner/                # /topner/           — 11-way NER slicing
├── app_top_yesterday/          # /topyesterday/     — trending works / people
├── app_top_research/           # /topresearch/      — full-text search + sentiment
│
├── app_user_keyword/                   # /userkeyword/          — keyword lookup + time series
├── app_user_keyword_association/       # /userkeyword_assoc/    — related words + same-paragraph
├── app_user_keyword_sentiment/         # /userkeyword_senti/    — sentiment distribution + trend
│
├── app_sentiment_bert/         # /sentiment/        — live BERT sentiment classifier
├── app_news_rcmd_bert/         # /rcmd/             — BERT-similarity news recommendation
│
├── app_netflix/                # /netflix/          — Netflix title mention view
├── app_stream/                 # /stream/           — streaming-service leaderboard
├── app_correlation/            # /correlation/      — Pearson correlation of two keywords
│
└── app_taipei_mayor/           # (not registered in urls.py — experimental)
```

Every app follows the standard Django layout (`models.py` usually empty,
`views.py`, `urls.py`, `templates/<app>/home.html`, `dataset/`).

---

## App Anatomy

### Aggregate-view apps (inherit from the midterm project)

#### 1. `app_top_keyword` — `/topword/`
- **API:** `POST api_get_cate_topword/` — `news_category`, `topk` → bar-chart labels/values + raw `(word, freq)` pairs.
- **Data:** `dataset/cna_news_topkey_with_category_via_token_pos.csv`
- Loads once, `del`s the DataFrame, keeps a `{category: [(w, f), ...]}` dict in memory.

#### 2. `app_top_person` — `/topperson/`
- **API:** `POST api_get_topPerson/` — `news_category`, `topk` → top-N most-mentioned people (from NER PERSON entities).
- **Data:** `dataset/news_top_person_by_category_via_ner.csv`

#### 3. `app_top_ner` — `/topner/`
- **API:** `POST api_get_ner_topword/` — `news_category` (index), `ner_value` (index), `topk` → `data_barchart` + proportionally scaled `data_cloud`.
- **Supported entities (11):** `EVENT, FAC, GPE, LANGUAGE, LAW, LOC, NORP, ORG, PERSON, PRODUCT, WORK_OF_ART`.
- **Data:** `dataset/news_topkey_by_ner_and_category.csv`

#### 4. `app_top_yesterday` — `/topyesterday/`
- **API:** `POST api_get_topYesterday/` — `news_category`, `topk` → trending WORK_OF_ART / PERSON in the previous period.
- **Data:** `dataset/popular-WORK_OF_ART-of-yesterday.csv`, `popular-PERSON-yesterday.csv`

#### 5. `app_top_research` — `/topresearch/`
- **API:** `POST api_get_topResearch/` — `title_or_content` → `{title, content, summary, sentiment}` arrays (precomputed).
- **Data:** `dataset/cna_news_preprocessed.csv` (pipe-separated, includes `sentiment` column).

### User-driven query apps (new in this capstone)

#### 6. `app_user_keyword` — `/userkeyword/`
- **API:** `POST api_get_top_userkey/` — `userkey` (whitespace-split), `cate`, `cond` (`and`/`or`), `weeks` → `{key_occurrence_cat, key_freq_cat, key_time_freq}`.
- **Data:** `dataset/cna_news_200_preprocessed.csv` (pipe-separated).
- **Behaviour:** filters the last N weeks and matches on the `tokens_v2` column (Boolean AND/OR), then reports per-category article count, keyword frequency, and a daily time series (Chart.js line data).

#### 7. `app_user_keyword_association` — `/userkeyword_assoc/`
- **API:** `POST api_get_userkey_associate/` — same inputs as above → `{num_articles, newslinks, related_words, same_paragraph, clouddata}`.
- **Data:** reuses `df` from `app_user_keyword.views` (imported directly) to avoid loading the CSV twice.
- **Behaviour:** aggregates the top-20 co-occurring `top_key_freq` entries into a scaled word cloud, extracts the paragraphs where the query keyword(s) appear together, and returns up to 25 news links with thumbnails.

#### 8. `app_user_keyword_sentiment` — `/userkeyword_senti/`
- **API:** `POST api_get_userkey_sentiment/` — `userkey`, `cate`, `cond`, `weeks` → `{sentiCount, data_pos, data_neg}`.
- **Data:** `dataset/news_dataset_preprocessed_for_django.csv`
- **Behaviour:** classifies precomputed article sentiment scores into positive (`>= 0.6`), negative (`<= 0.4`), neutral, then returns daily (`<= 4` weeks) or weekly (`> 4` weeks) time series suitable for Chart.js.

#### 9. `app_correlation` — `/correlation/`
- **API:** `POST api_get_corr_data/` — `userkey1`, `userkey2` (both whitespace-split) → `{pearson_coef, p_value, a_line_xy_data, b_line_xy_data}`.
- **Data:** `dataset/news_dataset_preprocessed_for_django.csv`
- **Behaviour:** builds two daily-frequency time series for the two keyword sets over the last 12 weeks and computes Pearson correlation via `scipy.stats.pearsonr`.

### BERT-powered apps

#### 10. `app_sentiment_bert` — `/sentiment/`
- **API:** `POST api_get_sentiment/` — `input_text` → `{Negative: p, Positive: p}` (softmax probabilities).
- **Model:** `clhuang/albert-sentiment` (Hugging Face), loaded via `AutoModelForSequenceClassification.from_pretrained(...)` at module import.
- **No dataset** — this is a live classifier over user text; the folder contains a `my-best-model/` placeholder for a locally trained alternative.

#### 11. `app_news_rcmd_bert` — `/rcmd/`
- **APIs:**
  - `POST api_query_keyword_cate_news/` — `category`, `input_keywords` → 4 sampled latest news matching the keywords in that category.
  - `POST api_news_content/` — `item_id` → `{news_content, related_news}` (the top-2 most similar articles).
  - `POST api_save_comment/` — `item_id`, `comment` → writes the comment back into the CSV.
- **Data:** `dataset/cna_news_200_preprocessed.csv` (pipe-separated) + `dataset/news_sim_martrix.npy` (precomputed BERT cosine-similarity matrix; recommendations are just top-k lookups).

### Domain-specific comparison apps

#### 12. `app_netflix` — `/netflix/`
- Renders `app_netflix/home.html`, seeded with a `dict(list(df.values))` context built from a CSV of Netflix-title mention counts. No JSON API — it's a static leaderboard-style page.

#### 13. `app_stream` — `/stream/`
- **API:** `POST api_get_stream_data/` — returns the whole preloaded dict (streaming-service leaderboard) as JSON.
- Same pattern as `app_taipei_mayor` from the midterm repo (a "pk"-style comparison), but reused for streaming platforms.

`app_taipei_mayor/` is present on disk but **not** registered in
`INSTALLED_APPS` or `urls.py`, so it is not served.

---

## Data Flow

```
raw CNA news
    │
    │  (offline notebooks, not in repo)
    │  tokenisation, POS, spaCy NER, sentiment scoring,
    │  BERT embedding + cosine similarity, per-category
    │  top-N aggregation
    ▼
preprocessed CSVs (+ .npy similarity matrix)  →  committed under
                                                  app_*/dataset/
    │
    │  Django start-up: each app's views.py loads its own
    │  CSV into module-level `data` dict or `df` DataFrame
    │  (some apps import `df` from a sibling app to save RAM)
    ▼
in-process pandas structures
    │
    │  POST /<app>/api_*/  (jQuery form-encoded)
    ▼
handler filters by (date-range, category, keyword AND/OR)  or
                   (item_id → matrix lookup)  or
                   (text → BERT softmax)
    │
    ▼
JsonResponse → frontend Chart.js bar / line / cloud / list
```

Each app prints a load-confirmation line on start-up
(e.g. `app_userkey_sentiment was loaded!`) so any CSV-missing failure
surfaces at process boot, not on the first request.

---

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.6+ (3.8 recommended) | matches the Django 2.2 window |
| Web framework | **Django 2.2 LTS** | course-pinned; stable ORM + routing |
| Database | **SQLite 3** | only used for Django auth; app data lives in CSV |
| Data processing | **pandas**, **NumPy** | vectorised CSV filtering |
| Stats | **SciPy** (`scipy.stats.pearsonr`) | correlation coefficient |
| NLP / ML | **transformers**, **torch** | BERT-family sentiment (`clhuang/albert-sentiment`) |
| Similarity | precomputed `.npy` cosine matrix | avoid live BERT inference per request |
| CORS | **django-cors-headers** | allow API calls from other origins during dev |
| Frontend | **Bootstrap 4**, **jQuery**, **Chart.js** | loaded from CDN inside each `home.html` |
| Deploy | **gunicorn** / any WSGI host | not shipped with a `requirements.txt` — install manually |

No pinned `requirements.txt` is committed. Suggested install:

```bash
pip install "django==2.2.28" "django-cors-headers==3.7.0" \
            pandas numpy scipy
# Only needed for the two BERT-backed apps
pip install torch transformers
```

---

## Requirements

- **Python 3.6+** (3.8 recommended for pandas/torch wheels)
- **pip** and a virtualenv (Django 2.2 pins are incompatible with newer
  ecosystems — isolate this project)
- ~200 MB free for the BERT model download (`clhuang/albert-sentiment`)
- ~50 MB for the shipped CSVs (some may need to be regenerated — see
  [Data Prerequisites](#data-prerequisites))
- Optional GPU (not required — the code uses CPU by default)

---

## Configuration

Everything lives in `website_configs/settings.py`:

| Setting | Value | Notes |
|---|---|---|
| `DEBUG` | `True` | flip to `False` for production |
| `ALLOWED_HOSTS` | `['*']` | wildcard — restrict for production |
| `SECRET_KEY` | hard-coded string | **rotate before deploying** |
| `DATABASES.default.ENGINE` | `django.db.backends.sqlite3` | file at `db.sqlite3` |
| `INSTALLED_APPS` | 13 project apps + `corsheaders` + Django defaults | |
| `CORS_ORIGIN_ALLOW_ALL` | `True` | allow all origins during dev |
| `TIME_ZONE` | `UTC` | |
| `LANGUAGE_CODE` | `en-us` | UI content itself is in Traditional Chinese |
| `STATIC_URL` | `/static/` | each app serves its own static assets |

No `.env` is expected. If you introduce one, the Hugging Face model call
in `app_sentiment_bert/views.py` is a good candidate to make
configurable (model name, cache dir).

---

## Running Locally

```bash
# 1. Clone
git clone https://github.com/Elainedu/Big-data-analytics-with-AI.git
cd Big-data-analytics-with-AI

# 2. Virtualenv
python -m venv venv
venv\Scripts\activate         # Windows
# source venv/bin/activate    # macOS / Linux

# 3. Install core stack
pip install "django==2.2.28" "django-cors-headers==3.7.0" pandas numpy scipy

# 4. (Optional) install BERT stack for /sentiment/ and /rcmd/
pip install torch transformers

# 5. Migrate Django's built-in tables
python manage.py migrate

# 6. Run the dev server (first launch downloads the Hugging Face model
#    — expect ~200 MB, cached under ~/.cache/huggingface/)
python manage.py runserver
```

Then browse to any of:

- <http://127.0.0.1:8000/topword/>
- <http://127.0.0.1:8000/topner/>
- <http://127.0.0.1:8000/topperson/>
- <http://127.0.0.1:8000/topyesterday/>
- <http://127.0.0.1:8000/topresearch/>
- <http://127.0.0.1:8000/userkeyword/>
- <http://127.0.0.1:8000/userkeyword_assoc/>
- <http://127.0.0.1:8000/userkeyword_senti/>
- <http://127.0.0.1:8000/correlation/>
- <http://127.0.0.1:8000/sentiment/>
- <http://127.0.0.1:8000/rcmd/>
- <http://127.0.0.1:8000/netflix/>
- <http://127.0.0.1:8000/stream/>

You should see console lines like `Loading app bert sentiment
classification.` and `app Bert based news recommendation was loaded!`
during start-up.

---

## Data Prerequisites

The repo ships small CSVs for the aggregate-view apps. The larger files
may need to be sourced separately (they are typically excluded via
`.gitignore` for size reasons):

| File | Used by | Notes |
|---|---|---|
| `app_top_research/dataset/cna_news_preprocessed.csv` | `app_top_research` | pipe-separated; full articles + summaries + sentiment |
| `app_user_keyword/dataset/cna_news_200_preprocessed.csv` | `app_user_keyword`, `app_user_keyword_association`, `app_news_rcmd_bert` | pipe-separated; needs `date`, `category`, `content`, `tokens_v2`, `top_key_freq`, `title`, `link`, `photo_link`, `comment`, `item_id` columns |
| `app_user_keyword_sentiment/dataset/news_dataset_preprocessed_for_django.csv` | `app_user_keyword_sentiment`, `app_correlation` | pipe-separated; needs a numeric `sentiment` column in `[0, 1]` |
| `app_news_rcmd_bert/dataset/news_sim_martrix.npy` | `app_news_rcmd_bert` | precomputed cosine similarity matrix aligned with the CSV row order |
| `app_sentiment_bert/my-best-model/` | (optional) | placeholder if you want to load a locally fine-tuned model instead of the Hugging Face default |

All file paths are **hard-coded relative to the project root** inside
each `views.py`, so always run `python manage.py runserver` from the
repo root.

---

## Deployment Notes

```bash
gunicorn website_configs.wsgi:application \
    --bind 0.0.0.0:8000 --workers 3 --timeout 120
```

The `--timeout 120` matters: the first request after boot may still
finish loading the Hugging Face model.

Before shipping to production:

1. Set `DEBUG = False` and lock `ALLOWED_HOSTS` to real host names.
2. Rotate `SECRET_KEY` (the tracked one is a dev placeholder).
3. Re-enable CSRF on the API endpoints — every `api_*` view is
   currently decorated with `@csrf_exempt` for jQuery convenience.
4. Configure a real static-file setup (`STATIC_ROOT` +
   `collectstatic`).
5. Pin `torch` and `transformers` versions; they are heavy and
   version-sensitive. Use CPU-only wheels
   (`torch --index-url https://download.pytorch.org/whl/cpu`) to
   halve the image size if you don't need GPU.
6. If you serve behind nginx, allow request body sizes large enough
   for the recommendation content POSTs (~few KB).
7. Consider replacing the shared-mutable `df` writes in
   `app_news_rcmd_bert.save_comment()` (which mutates the in-memory
   DataFrame *and* rewrites the CSV on every comment) with a proper
   database write — it is not safe under multi-worker gunicorn.

---

## What's Not in the Repo

| Excluded | Why | Where to get it |
|---|---|---|
| `.env` | secrets (not currently used, but reserve the name) | create locally if needed |
| `venv/` | per-machine | `python -m venv venv` |
| Large full-text CSVs | size | rebuild from the course's preprocessing pipeline |
| Precomputed similarity matrix (`news_sim_martrix.npy`) | large binary | regenerate with BERT embedding + cosine similarity, then `np.save` |
| Locally trained BERT weights (`app_sentiment_bert/my-best-model/`) | large binary | the app falls back to `clhuang/albert-sentiment` from Hugging Face |
| `__pycache__/`, `*.pyc` | build artifacts | regenerated on run |

---

## License

Released for **educational use**. Built as a graduate-level capstone for
a Big Data / Business Intelligence course; feel free to read, run, and
adapt for study.
