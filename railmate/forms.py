from django.contrib.auth.models import User
from django import forms
from railmate.models import Profile, Trip


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', 'birth_date')


class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ('source', 'destination', 'date', 'time', 'deviation', 'subscription', 'compensation')