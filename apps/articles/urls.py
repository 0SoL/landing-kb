from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.article_list, {'category_slug': 'novosti'}, name='news_list'),
    path('<slug:slug>/', views.article_detail, name='detail'),
]
