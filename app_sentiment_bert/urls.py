from django.urls import path
from app_sentiment_bert import views

app_name = 'namespace_sentiment_bert'

urlpatterns = [
    path('', views.home, name='home'),
    path('api_get_sentiment/', views.api_get_sentiment),
]
