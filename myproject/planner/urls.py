from django.urls import path
from . import views

urlpatterns = [
    path('', views.planner_index, name='planner_index'),
    path('ai_suggestions/', views.ai_suggestions, name='ai_suggestions'),
    path('ai_create/', views.ai_create, name='ai_create'),
    path('get_previous_dialogue/', views.get_previous_dialogue, name='get_previous_dialogue'),
    path('merge_temp_events/', views.merge_temp_events, name='merge_temp_events'),
    path('get_temp_long_events/', views.get_temp_long_events, name='get_temp_long_events'),
    path('add_to_ai_planning_time/', views.add_to_ai_planning_time, name='add_to_ai_planning_time'),
    path('delete_events_in_range/', views.delete_events_in_range, name='delete_events_in_range'),
]