from datetime import date

from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.models import User
from django import forms
from django.forms import SelectDateWidget
from django.forms.fields import DateField

from railmate.models import Profile, Message, Trip, Search


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileForm(forms.ModelForm):
    birth_date = forms.DateField(
        widget=SelectDateWidget(empty_label=('Year', 'Month', 'Day'), years=range(1900, date.today().year)))
    avatar = forms.ImageField(label=('h'),required=False, widget=forms.FileInput)

    class Meta:
        model = Profile
        fields = ('avatar', 'birth_date')


class MessageForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'style': 'width: 100%;'}), label='')

    class Meta:
        model = Message
        fields = ('content',)


class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ('source', 'destination', 'datetime', 'datetime_end', 'deviation', 'subscription', 'compensation')


class SearchForm(forms.ModelForm):
    class Meta:
        model = Search
        fields = ('source', 'destination', 'date', 'time',)


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
