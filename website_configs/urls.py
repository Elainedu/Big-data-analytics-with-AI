from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    # top keywords
    path('topword/', include('app_top_keyword.urls')),
    # app top persons
    path('topperson/', include('app_top_person.urls')),
    # top ner
    path('topner/', include('app_top_ner.urls')),
    # top yesterday
    path('topyesterday/', include('app_top_yesterday.urls')),
    #top research
    path('topresearch/', include('app_top_research.urls')),
     # user keyword analysis
    path('userkeyword/', include('app_user_keyword.urls')),
    # full text search and associated keyword display
    path('userkeyword_assoc/', include('app_user_keyword_association.urls')),
    # Sentiment analysis
    path('sentiment/', include('app_sentiment_bert.urls')),
    # user keyword sentiment 
    path('userkeyword_senti/', include('app_user_keyword_sentiment.urls')),
    # user keyword sentiment 
    path('netflix/', include('app_netflix.urls')),
    # user keyword sentiment 
    path('stream/', include('app_stream.urls')),
    path('correlation/', include('app_correlation.urls')),
    # news recommendation with bert
    path('rcmd/', include('app_news_rcmd_bert.urls')),

]
