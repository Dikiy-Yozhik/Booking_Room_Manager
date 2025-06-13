# bd/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('calendar/', views.calendar_view, name='calendar'),
    path('book/', views.book_room, name='book_room'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('profile/', views.profile_view, name='profile'),
]