from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import Reservation, RestaurantSettings


class ReservationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop('language', 'ar')
        self.site = kwargs.pop('site', None) or RestaurantSettings.load()
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        self.fields['date'].widget.attrs.update({
            'min': today.isoformat(),
            'max': (today + timedelta(days=self.site.max_reservation_days_ahead)).isoformat(),
        })
        self.fields['time'].widget.attrs['step'] = self.site.reservation_slot_minutes * 60
        self.fields['guests'].widget.attrs['min'] = 1
        required_message = 'هذا الحقل مطلوب.' if self.language == 'ar' else 'This field is required.'
        for field in self.fields.values():
            field.error_messages['required'] = required_message

    class Meta:
        model = Reservation
        fields = ['full_name', 'phone', 'date', 'time', 'guests', 'occasion', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'autocomplete': 'name'}),
            'phone': forms.TextInput(attrs={'autocomplete': 'tel', 'inputmode': 'tel'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'guests': forms.NumberInput(attrs={'min': 1, 'max': 50}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_date(self):
        reservation_date = self.cleaned_data['date']
        today = timezone.localdate()
        if reservation_date < today:
            message = 'لا يمكن الحجز في تاريخ سابق.' if self.language == 'ar' else 'Reservations cannot be made in the past.'
            raise forms.ValidationError(message)
        if reservation_date > today + timedelta(days=self.site.max_reservation_days_ahead):
            message = (
                f'يمكن الحجز خلال {self.site.max_reservation_days_ahead} يومًا فقط.'
                if self.language == 'ar'
                else f'Reservations can only be made {self.site.max_reservation_days_ahead} days ahead.'
            )
            raise forms.ValidationError(message)
        return reservation_date

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        allowed = set('+ -()')
        if any(not character.isdigit() and character not in allowed for character in phone):
            message = 'أدخل رقم جوال صحيحًا.' if self.language == 'ar' else 'Enter a valid phone number.'
            raise forms.ValidationError(message)
        digits = ''.join(character for character in phone if character.isdigit())
        if not 7 <= len(digits) <= 15:
            message = 'أدخل رقم جوال صحيحًا.' if self.language == 'ar' else 'Enter a valid phone number.'
            raise forms.ValidationError(message)
        return digits

    def clean(self):
        cleaned_data = super().clean()
        reservation_date = cleaned_data.get('date')
        reservation_time = cleaned_data.get('time')
        now = timezone.localtime()
        if reservation_date == now.date() and reservation_time and reservation_time <= now.time().replace(tzinfo=None):
            message = 'لا يمكن الحجز في وقت مضى.' if self.language == 'ar' else 'Reservations cannot be made in the past.'
            self.add_error('time', message)
        if reservation_time:
            opening = self.site.reservation_open_time
            closing = self.site.reservation_close_time
            within_hours = (
                opening == closing
                or (opening < closing and opening <= reservation_time <= closing)
                or (opening > closing and (reservation_time >= opening or reservation_time <= closing))
            )
            if not within_hours:
                message = (
                    f'الحجز متاح بين {opening.strftime("%H:%M")} و{closing.strftime("%H:%M")}.'
                    if self.language == 'ar'
                    else f'Reservations are available between {opening.strftime("%H:%M")} and {closing.strftime("%H:%M")}.'
                )
                self.add_error('time', message)
            minutes = reservation_time.hour * 60 + reservation_time.minute
            if minutes % self.site.reservation_slot_minutes:
                message = (
                    f'اختر وقتًا بفواصل {self.site.reservation_slot_minutes} دقيقة.'
                    if self.language == 'ar'
                    else f'Choose a time in {self.site.reservation_slot_minutes}-minute intervals.'
                )
                self.add_error('time', message)
        if reservation_date and reservation_time and not self.errors:
            active_count = Reservation.objects.filter(
                date=reservation_date,
                time=reservation_time,
                status__in=['new', 'contacted', 'confirmed'],
            ).exclude(pk=self.instance.pk).count()
            if active_count >= self.site.max_reservations_per_slot:
                message = (
                    'هذه الفترة ممتلئة، اختر وقتًا آخر.'
                    if self.language == 'ar'
                    else 'This time slot is full. Please choose another time.'
                )
                self.add_error('time', message)
        return cleaned_data
