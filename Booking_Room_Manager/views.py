

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Booking_Room_Manager.models import Room, Booking, TimeSlot
from Booking_Room_Manager.forms import BookingForm
from django.utils import timezone
from datetime import datetime
from datetime import timedelta, time

__all__ = (
    "calendar_view",
    "book_room",
    "cancel_booking",
    "profile_view",
    "home",
)


def home(request):
    # Проверяем, авторизован ли пользователь
    is_authenticated = request.user.is_authenticated

    context = {
        'is_authenticated': is_authenticated,
        'is_student': is_authenticated and not request.user.is_staff,
        'is_teacher': is_authenticated and hasattr(request.user, 'teacher_profile'),
        'is_admin': is_authenticated and request.user.is_staff,
    }
    return render(request, 'Booking_Room_Manager/home.html', context)

def calendar_view(request):
    rooms = Room.objects.all()
    today = timezone.now().date()
    times = [time(h, 0) for h in range(9, 18)]  # 9:00 - 17:00
    bookings = Booking.objects.filter(date=today, is_active=True)

    time_slots = []

    for t in times:
        row = {'time': t.strftime("%H:%M"), 'rooms': []}  
        for room in rooms:
            is_booked = bookings.filter(room=room, start_time=t).exists()
            row['rooms'].append({
                'name': room.name,
                'id': room.id,
                'booked': is_booked
            })
        time_slots.append(row)

    context = {
        'time_slots': time_slots,
        'today': today
    }

    return render(request, 'Booking_Room_Manager/calendar.html', context)

@login_required
def book_room(request):
    initial = {}

    room_id = request.GET.get('room')
    selected_time_str = request.GET.get('time')

    if room_id:
        initial['room'] = room_id

    if selected_time_str:
        today = timezone.now().date()
        try:
            parsed_time = datetime.strptime(selected_time_str, "%H:%M").time()
        except ValueError:
            try:
                parsed_time = datetime.strptime(selected_time_str, "%I %p").time()
            except ValueError:
                parsed_time = None

        if parsed_time:
            initial['date'] = today
            initial['start_time'] = parsed_time
            initial['end_time'] = (
                datetime.combine(today, parsed_time) + timedelta(hours=1)
            ).time()

    form = BookingForm(initial=initial)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            try:
                booking.save()
                messages.success(request, "Комната успешно забронирована!")
                return redirect('profile')
            except Exception as e:
                messages.error(request, str(e))

    return render(request, 'Booking_Room_Manager/book_form.html', {'form': form})
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.cancel_booking()
    messages.success(request, "Бронь успешно отменена.")
    return redirect('profile')

@login_required
def profile_view(request):
    bookings = Booking.objects.filter(
        user=request.user, is_active=True).order_by('-date')

    return render(request, 'Booking_Room_Manager/profile.html', {'bookings': bookings})