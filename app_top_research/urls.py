from django.urls import path
from . import views

app_name = "app_top_research"

urlpatterns = [
    path('', views.home, name='home'),
    path('api_get_topResearch/', views.api_get_topResearch, name='api_get_topResearch'),
    path('search_news/', views.search_news, name='search_news'),
]
