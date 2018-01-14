from datetime import date

from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.models import User
from django import forms
from django.forms import SelectDateWidget
from django.forms.fields import DateField

from railmate.models import Profile, Message, Trip


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileForm(forms.ModelForm):
    birth_date = forms.DateField(
        widget=SelectDateWidget(empty_label=('Year', 'Month', 'Day'), years=range(1900, date.today().year)))
    avatar = forms.ImageField()

    class Meta:
        model = Profile

        fields = ('avatar', 'email', 'birth_date')


class MessageForm(forms.ModelForm):
    content = forms.TextInput()

    class Meta:
        model = Message
        fields = ('content', 'recipient')
        labels = {'content': ''}


class TripForm(forms.ModelForm):
    content = forms.TextInput()

    class Meta:
        model = Trip
        fields = {'user',
                  'source',
                  'destination',
                  'datetime',
                  'datetime_end',
                  'tripnumber',
                  'compensation',
                  'subscription',
                  'deviation',
                  'companions',
                  'max_companions',
                  'station_list',
                  }
