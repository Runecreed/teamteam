from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, Template, loader, RequestContext

from django.contrib.auth import logout as logout_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

from railmate.forms import ProfileForm, UserForm, MessageForm
from railmate.models import Profile, Message, Trip, Fellow_passengers
from railmate.services import NS, MessagingService


def home(request):
    trip_list = []  # empty list initially
    station_list = []
    form = NS().station_list()

    if request.method == 'GET' and 'getTrain' in request.GET:  # the user wants to search for possible trips with CreateTrip form
        searchQuery = request.GET.urlencode()  # debug var
        source = request.GET.get('source', '')
        destination = request.GET.get('destination', '')
        parameters = [source, destination]
        results = NS().trip_list(parameters)
        station_list = results[
            'station_intermediate']  # List of Intermediate stations between source and destionation, IE: Eindhoven -- Weert -- Roermond -- Sittard ...
        trip_list = results[
            'trips']  # List representation holding trips, each entry in the list trip_list[0] represents ONE possible trip with a lot of info that you can display.
        return render(request, 'railmate/createTripShow.html',
                      {'stations': form, 'trip_list': trip_list, 'station_list': station_list})

    if request.method == 'POST':  # user wants to post a new Trip! woo
        Lol = "DO STUF HERE NUB"

    # User is visiting home page.

    return render(request, 'railmate/index.html',
                  {'stations': form, 'trip_list': trip_list, 'station_list': station_list})


# User filled in the form and presses Search
def home_search(request):
    searchQuery = request.GET.urlencode()  # debug var

    source = request.GET.get('source', '')
    destination = request.GET.get('destination', '')
    date = request.GET.get('date', '')
    recurrence = request.GET.get('recurrence', '')
    deviation = request.GET.get('deviation', '')
    time = request.GET.get('time', '')

    search = {'source': source, 'destination': destination, 'date': date, 'recurrence': recurrence,
              'deviation': deviation, 'time': time}
    results = 'Not implemented yet'
    # return results
    form = NS().station_list()
    return render(request, 'railmate/trips.html', {'form': form, 'search_results': search})


# User presses POST button to create a trip
# # REDUNDANT - NOT USED ANYMORE
# def home_create(request):
#     searchQuery = request.GET.urlencode()  # debug var
#     source = request.GET.get('source', '')
#     destination = request.GET.get('destination', '')
#     parameters = [source, destination]
#
#     trip_list = NS().trip_list(parameters)
#
#     response = HttpResponse("To be implemented, probably want to redirect to the home page after inserting to DB")
#     return response


def user_page(request, user_id):
    return HttpResponse("You're looking at user %s." % user_id)


def login_user(request):
    logout(request)
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
    return render(request, 'railmate/login.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)

            login(request, user)
            return redirect('/account')
    else:
        form = UserCreationForm()
    return render(request, 'railmate/signup.html', {'form': form})


@login_required
def editAccount(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # messages.success(request, _('Your profile was successfully updated!'))
            return redirect('/account')
        else:
            messages.error(request, ('Please correct the error below.'))
    else:
        profile = Profile.objects.filter(user=request.user)
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'railmate/editacount.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'avatar':profile
    })


@login_required
def account(request):
    ride_along = Fellow_passengers.objects.filter(user= request.user)
    contacts = Profile.objects.all()
    #passengers moet lijst met user waarme je in een conversatie zit
    trip_info = Trip.objects.filter(user=request.user,date__gte=date.today()).order_by('date')
    trip_history = Trip.objects.filter(user=request.user).order_by('-date').exclude(date__gte=date.today())
    trip_info_history = Trip.objects.filter(user=request.user).order_by('-date')
    user_info = Profile.objects.get(user=request.user)
    if user_info.birth_date is None:
        user_info.age = '-'
    else:
        user_info.age = calculate_age(user_info.birth_date)
    return render(request, 'railmate/account.html', {'user_info': user_info,'trip_info': trip_info,'contacts':contacts,'trip_history':trip_history,'ride_along':ride_along})


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def logout(request):
    logout_user(request)
    return redirect('/')


def messages(request):
    # conversation = Message.objects.get(user=request.user)
    if request.method == 'POST':
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            msg = message_form.save(commit=False)
            msg.sender = request.user
            MessagingService().send_message(msg.sender, msg.recipient, msg.content)
            return redirect('/account')
    else:
        message_form = MessageForm(instance=request.user)
    return render(request, 'railmate/messages.html', {
        # 'messages': conversation,
        'message_form': message_form
    })
def trip_edit(request,trip_id):
    trip_info = Trip.objects.get(pk=trip_id)
    return render(request, 'railmate/edit_trip.html', {'trip_info': trip_info})
def trip_delete(request,trip_id):
    trip_info = Trip.objects.get(pk=trip_id)
    if trip_info.user == request.user:
        trip_info.delete()
    return redirect(account)
def add_passenger(request,trip_id):
    user_id = request.POST['passanger']
    trip_info = Trip.objects.get(pk=trip_id)
    if trip_info.user == request.user and trip_info.fellow_passengers_set.count() < 4:
        new_passenger = Fellow_passengers.objects.create(trip_id = trip_info, user = User.objects.get(pk=user_id))
        new_passenger.save()

    return redirect(account)

def remove_passenger(request, passenger_id):
    passenger = Fellow_passengers.objects.get(pk=passenger_id)
    if passenger.trip_id.user == request.user:
        passenger.delete()
    return redirect(account)