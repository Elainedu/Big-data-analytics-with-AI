# Big Data Analytics with AI

> A Django-based news analytics platform that mines keywords, entities, sentiment, and content recommendations from a news corpus.

[![Django](https://img.shields.io/badge/Django-2.2-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Educational%20Use-yellow.svg)](#license)

Repository: <https://github.com/Elainedu/Big-data-analytics-with-AI>

## Overview

This project is the capstone deliverable for an academic Big Data / Business Intelligence course. It bundles multiple Django apps under a single site, each responsible for a different analytical view of the same news dataset. Views range from simple top-keyword charts to BERT-based sentiment scoring and news recommendation.

The platform is data-heavy but stateless: each app loads its own preprocessed CSV (and optional model artifact) at request time, renders an interactive Bootstrap/Chart.js page, and exposes a small JSON API for the frontend.

## Tech Stack

- **Framework:** Django 2.2
- **Language:** Python 3.6+
- **Database:** SQLite 3 (default `db.sqlite3`)
- **Data processing:** pandas, NumPy
- **NLP / ML:** BERT-based sentiment and recommendation models (loaded per-app)
- **CORS:** `django-cors-headers`
- **Frontend:** Bootstrap 4, jQuery, Chart.js
- **Templates:** Django templates with a shared `navbar.html`

## Features / Apps

Thirteen apps are registered in `website_configs/settings.py` and routed in `website_configs/urls.py`:

| App | URL prefix | What it does |
|-----|------------|--------------|
| `app_top_keyword` | `/topword/` | Top keywords per news category, rendered as bar chart + list. |
| `app_top_person` | `/topperson/` | Ranking of most-mentioned people per category (via NER). |
| `app_top_ner` | `/topner/` | Top named entities filtered by NER type (PERSON, ORG, GPE, LOC, EVENT, WORK_OF_ART, PRODUCT, LAW, LANGUAGE, FAC, NORP). |
| `app_top_yesterday` | `/topyesterday/` | Trending works / people from the previous period. |
| `app_top_research` | `/topresearch/` | Full-text news search with summary and sentiment tagging. |
| `app_user_keyword` | `/userkeyword/` | User-supplied keyword lookup returning frequency data. |
| `app_user_keyword_association` | `/userkeyword_assoc/` | Association / co-occurrence view for a user-supplied keyword. |
| `app_sentiment_bert` | `/sentiment/` | BERT-based sentiment classification for arbitrary text. |
| `app_user_keyword_sentiment` | `/userkeyword_senti/` | Sentiment distribution over articles matching a user keyword. |
| `app_netflix` | `/netflix/` | Netflix-title mention analysis across the news corpus. |
| `app_stream` | `/stream/` | Streaming-service mention analysis and comparison. |
| `app_correlation` | `/correlation/` | Correlation view between keywords / topics over time. |
| `app_news_rcmd_bert` | `/rcmd/` | BERT-based news recommendation with per-article content view and comment saving. |

Additional experimental app folders exist on disk (e.g. `app_taipei_mayor`) but are not registered in `INSTALLED_APPS` and are not served.

## Getting Started

### 1. Clone

```bash
git clone https://github.com/Elainedu/Big-data-analytics-with-AI.git
cd Big-data-analytics-with-AI
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

No pinned `requirements.txt` ships with the repo; install the core stack manually:

```bash
pip install "django==2.2" pandas django-cors-headers
```

For the BERT-powered apps (`app_sentiment_bert`, `app_news_rcmd_bert`) you will additionally need:

```bash
pip install torch transformers scikit-learn
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Run the development server

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/topword/> (or any of the URL prefixes in the table above) in a browser.

## Project Structure

```
Big-data-analytics-with-AI/
├── manage.py
├── db.sqlite3
├── templates/                        # shared templates (navbar, etc.)
├── website_configs/                  # Django project (settings, urls, wsgi)
├── app_top_keyword/                  # top-keyword analytics
├── app_top_person/                   # top-person ranking
├── app_top_ner/                      # NER-based entity analytics
├── app_top_yesterday/                # previous-period trending
├── app_top_research/                 # full-text search + summary
├── app_user_keyword/                 # user keyword lookup
├── app_user_keyword_association/     # keyword co-occurrence
├── app_sentiment_bert/               # BERT sentiment classifier
├── app_user_keyword_sentiment/       # sentiment by keyword
├── app_netflix/                      # Netflix mention analysis
├── app_stream/                       # streaming-service analysis
├── app_correlation/                  # keyword correlation over time
├── app_news_rcmd_bert/               # BERT news recommendation
└── app_taipei_mayor/                 # experimental (not registered)
```

Each app follows the standard Django layout (`models.py`, `views.py`, `urls.py`, `templates/<app>/`) and ships its own `dataset/` directory with preprocessed CSVs.

## Notes

- This is an **academic project** built as a capstone for a graduate-level Big Data / Business Intelligence course. It is intended for learning and demonstration, not production deployment.
- The default settings run with `DEBUG = True` and `ALLOWED_HOSTS = ['*']`. Do not deploy as-is.
- The database is SQLite (`db.sqlite3`). A secondary `db_1.sqlite3` snapshot is kept alongside it.
- Large model artifacts (BERT weights, tokenizer files) are excluded via `.gitignore` and must be obtained or trained separately before the BERT-backed apps will work.
- CSRF is disabled on several API endpoints for convenience; re-enable it before exposing the site publicly.

## License

Released for **Educational Use**. Feel free to read, run, and adapt the code for coursework or personal study.
