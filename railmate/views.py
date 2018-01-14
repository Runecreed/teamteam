from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, Template, loader, RequestContext

from django.contrib.auth import logout as logout_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.db.models import Q

# Create your views here.
from django.utils import formats

from railmate.forms import ProfileForm, UserForm, TripForm
from railmate.models import Profile, Trip

from railmate.services import NS


def home(request):

    if request.method == "POST":
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.user = request.user #moet nog aangepast worden naar de goede user (misschien)
            trip.companions = 0
            trip.max_companions = 3
            trip.save()
            return redirect('/', pk=trip.pk)
        else:
            form = TripForm()
        return render(request, 'railmate/index.html', {'form': form})

    # Required :: Form must have keys 'source', with a list of sources undearneatha:: form = {'station': ['Eindhoven', 'Maastricht', ...], 'destination: ..}
    # refer to it in the template as : form.source  --- gets the list of sources
    # form = {'station': ['Eindhoven', 'Maastricht']}

    form = NS().station_list()
    return render(request, 'railmate/index.html', {'form': form})


# User filled in the form and presses Search
def home_search(request):
    #searchQuery = request.GET.urlencode()  # debug var

    source = request.GET.get('source', '')
    destination = request.GET.get('destination', '')
    date = request.GET.get('date', '')
    #recurrence = request.GET.get('recurrence', '')
    #deviation = request.GET.get('deviation', '')
    time = request.GET.get('time', '')

    #search = {'source': source, 'destination': destination, 'date': date, 'recurrence': recurrence,
              #'deviation': deviation, 'time': time}
    #results = 'Not implemented yet'
    # return results
    form = NS().station_list()
    #return render(request, 'railmate/trips.html', {'form': form, 'search_results': search})
    trips = Trip.objects.all().filter(
        Q(source=source)
    )
    return render(request, 'railmate/trips.html', {'form': form, 'trips': trips})

# User presses POST button to create a trip
def home_create(request):
    form = NS().station_list()

    response = HttpResponse("To be implemented, probably want to redirect to the home page after inserting to DB")
    return response


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
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # messages.success(request, _('Your profile was successfully updated!'))
            return redirect('profile')
        else:
            messages.error(request, ('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'railmate/editacount.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def account(request):
    user_info = Profile.objects.get(user=request.user)
    if (user_info.birth_date is None):
        user_info.age = '-'
    else:
        user_info.age = calculate_age(user_info.birth_date)
    return render(request, 'railmate/account.html', {'user_info': user_info})

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def logout(request):
    logout_user(request)
    return redirect('/')


@login_required
def messages(request):
    user_info = Profile.objects.get(pk=request.user)
    return render(request, 'railmate/messages.html')
