# bd/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room, Booking, TimeSlot
from .forms import BookingForm
from django.utils import timezone
from datetime import datetime
from datetime import timedelta, time

# Критерий 6: Календарь со слотами
# bd/views.py

def calendar_view(request):
    rooms = Room.objects.all()
    today = timezone.now().date()
    times = [time(h, 0) for h in range(9, 18)]  # 9:00 - 17:00

    # Получаем все временные слоты на неделю
    all_slots = TimeSlot.objects.filter(date__gte=today, date__lte=today + timedelta(days=6))

    # Получаем бронирования на те же дни
    bookings = Booking.objects.filter(date__gte=today, is_active=True)

    # Готовим данные для шаблона
    time_slots = []

    for t in times:
        row = {'time': t, 'rooms': []}
        for room in rooms:
            # Проверяем, есть ли бронь в этот день и время
            is_booked = bookings.filter(room=room, date=today, start_time=t).exists()

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

    return render(request, 'bd/calendar.html', context)

# bd/views.py
# bd/views.py

@login_required
def book_room(request):
    initial = {}

    # Получаем параметры из URL
    room_id = request.GET.get('room')
    selected_time = request.GET.get('time')

    if room_id:
        initial['room'] = room_id

    if selected_time:
        from datetime import datetime, timedelta
        today = datetime.now().date()
        initial['date'] = today
        initial['start_time'] = selected_time
        initial['end_time'] = (datetime.strptime(selected_time, "%H:%M") + timedelta(hours=1)).time()

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
            except ValidationError as e:
                messages.error(request, str(e))

    return render(request, 'bd/book_form.html', {'form': form})

# Критерий 8: Отмена брони
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.cancel_booking()
    messages.success(request, "Бронь успешно отменена.")
    return redirect('profile')

# Критерий 9: Профиль с бронями
@login_required
def profile_view(request):
    bookings = Booking.objects.filter(
        user=request.user, is_active=True).order_by('-date')

    return render(request, 'bd/profile.html', {'bookings': bookings})  # Убери 'templates/'