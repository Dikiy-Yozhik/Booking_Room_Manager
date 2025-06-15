# Booking_Room_Manager/urls.py

from django.urls import path
from Booking_Room_Manager import views

urlpatterns = [
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('book/', views.book_room, name='book_room'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('profile/', views.profile_view, name='profile_view'),
    path("", views.home, name="home"),
    path('booking/<int:booking_id>/reschedule/',
         views.reschedule_booking,
         name='reschedule_booking'),
    path('add-room/', views.add_room, name='add_room'),
path('export-bookings/', views.export_bookings, name='export_bookings'),
]