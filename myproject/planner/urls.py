from django.urls import path
from . import views

urlpatterns = [
    path('', views.planner_index, name='planner_index'),
    path('ai_suggestions/', views.ai_suggestions, name='ai_suggestions'),
]