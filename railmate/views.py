from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, Template, loader

from django.contrib.auth import logout as logout_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

# Create your views here.
from railmate.forms import UserForm, ProfileForm
from railmate.models import Profile

from railmate.services import NS


def home(request):
    # Required :: Form must have keys 'source', with a list of sources undearneatha:: form = {'station': ['Eindhoven', 'Maastricht', ...], 'destination: ..}
    # refer to it in the template as : form.source  --- gets the list of sources
    # form = {'station': ['Eindhoven', 'Maastricht']}

    form = NS().station_list()
    return render(request, 'railmate/index.html', {'form': form})


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
def home_create(request):
    form = NS().station_list()

    response = HttpResponse("To be implemented, probably want to redirect to the home page after inserting to DB")
    return response


def user_page(request, user_id):
    return HttpResponse("You're looking at user %s." % user_id)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
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
    return render(request, 'registration/base_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def account(request):
    user_info = Profile.objects.get(pk=request.user)
    return render(request, 'railmate/account.html')


def logout(request):
    logout_user(request)
    return redirect('/')


@login_required
def messages(request):
    user_info = Profile.objects.get(pk=request.user)
    return render(request, 'railmate/messages.html')

def create_trip(request):
    if request.method == "POST":
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.user = request.user
            trip.companions = 0
            trip.max_companions = 3
            trip.save()
            return redirect('railmate/index.html', pk=trip.pk)
        else:
            form = TripForm()
        return render(request, 'railmate/index.html', {'form': form})
