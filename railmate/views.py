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


def home(request):
    # Required :: Form must have keys 'source', with a list of sources undearneatha:: form = {'station': ['Eindhoven', 'Maastricht', ...], 'destination: ..}
    # refer to it in the template as : form.source  --- gets the list of sources
    form = {'station': ['Eindhoven', 'Maastricht']}
    return render(request, 'railmate/index.html',  {'form' : form})


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
