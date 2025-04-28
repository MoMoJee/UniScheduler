from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('home/', views.home, name='home'),
    path('user_register/', views.user_register, name='user_register'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('user_data/', views.user_data, name='user_data'),
    path('get_calendar/events/', views.get_events, name='get_events'),
    path('get_calendar/update_events/', views.update_events, name='update_events'),
    path('get_calendar/delete_event/', views.delete_event, name='delete_event'),
    path('get_calendar/create_event/', views.create_event, name='create_event'),
    path('get_calendar/create_events_group/', views.create_events_group, name='create_events_group'),
    path('get_calendar/update_events_group/', views.update_event_group, name='update_events_group'),
    path('get_calendar/delete_event_groups/', views.delete_event_groups, name='delete_event_groups'),
    path('get_calendar/import_events/', views.import_events, name='import_events'),
    path('get_calendar/resources/', views.get_resources, name='get_resources'),
    path("get_calendar/cal.ics", views.generate_ics, name="generate_ics"),
    path("get_calendar/subscribe_calendar/", views.subscribe_calendar, name="subscribe_calendar"),
    path("get_calendar/change_view/", views.change_view, name="change_view"),
    path("get_calendar/user_settings/", views.user_settings, name="user_settings"),
]
