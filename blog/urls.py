from django.urls import path
from . import views

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='blog_list'),
    path('categorie/<slug:category_slug>/', views.ArticleListView.as_view(), name='blog_category'),
    path('<slug:slug>/', views.ArticleDetailView.as_view(), name='blog_detail'),
]