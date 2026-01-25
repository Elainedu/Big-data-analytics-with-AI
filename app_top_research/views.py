from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

# 全局變量，存儲加載的數據
data = pd.DataFrame()

def load_data_topResearch():
    global data
    data = pd.read_csv('app_top_research/dataset/cna_news_preprocessed.csv',sep='|')
    print("Data loaded successfully!")

# 預先加載數據
load_data_topResearch()

def home(request):
    return render(request, 'app_top_research/home.html')

@csrf_exempt
def api_get_topResearch(request):
    search_keyword = request.POST.get('title_or_content')
    title, content, summary,sentiment = search_news(search_keyword)

    response = {
        'title': title,
        'content': content,
        'summary': summary, 
        'sentiment':sentiment
    }
    return JsonResponse(response)

def search_news(search_keyword):
   #找出索引值
    titles=[]
    contents=[]
    summary =[]
    sentiment=[]
    #print("get_select_news()--------2")
    df2=data.loc[(data['title'] == search_keyword)]
    index = df2.index
    print(index)
    #利用迴圈將找到的所印值中要的資料取出
    #print("get_select_news()--------3")
    for i in index:
        #找到的內容
        titles.append(data.at[i, "title"])
        print(i,"\n標題：\n",data.at[i, "title"])
        #print("get_select_news()--------4")
        contents.append(data.at[i, "content"])
        print("內容：\n",data.at[i, "content"],"\n")       
        summary.append(data.at[i, "summary"])
        sentiment.append(data.at[i, "sentiment"])
    return titles, contents, summary,sentiment



    


    
    # if request.method == 'POST':
    #     query = request.POST.get('query', '')
    #     matches = data[
    #         (data['title'].str.contains(query, case=False, na=False)) |
    #         (data['content'].str.contains(query, case=False, na=False))
    #     ]
    #     if not matches.empty:
    #         news = matches.iloc[0]
    #         sentiment_analysis = analyze_sentiment(news['content'])
    #         keywords_chart = plot_keywords_chart(eval(news['top_key_freq']))
    #         response = {
    #             'item_id': news['item_id'],
    #             'title': news['title'],
    #             'content': news['content'],
    #             'summary': news['summary'],
    #             'link': news['link'],
    #             'photo_link': news['photo_link'],
    #             'sentiment': sentiment_analysis,
    #             'keywords_chart': keywords_chart
    #         }
    #         return JsonResponse(response)
    #     else:
    #         return JsonResponse({'error': 'No news found matching the query.'})

# def analyze_sentiment(text):
#     blob = TextBlob(text)
#     return 'Positive' if blob.sentiment.polarity > 0 else 'Negative'

# def plot_keywords_chart(top_key_freq):
#     keywords, frequencies = zip(*top_key_freq)
#     plt.figure(figsize=(10, 5))
#     plt.bar(keywords, frequencies, color='blue')
#     plt.xlabel('Keywords')
#     plt.ylabel('Frequency')
#     plt.title('Keywords Frequency')
#     plt.xticks(rotation=45)
#     plt.tight_layout()
#     buf = io.BytesIO()
#     plt.savefig(buf, format='png')
#     plt.close()
#     return base64.b64encode(buf.getvalue()).decode('utf-8')
