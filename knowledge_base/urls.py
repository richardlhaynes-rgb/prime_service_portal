from django.urls import path
from service_desk import views

urlpatterns = [
    path('', views.kb_home, name='kb_home'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
]