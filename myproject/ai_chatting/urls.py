from django.urls import path
from . import views

urlpatterns = [
    path('', views.ai_chatting_index, name='ai_chatting_index'),
    path('chatting/', views.chatting, name='chatting'),
    path('test/', views.test, name='input_output')
]