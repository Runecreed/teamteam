from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


# Create your views here.

# Note that the routing REQUIRES you to return a HttpResponse, OR an exception. Everything done in between is free.

def home(request):
    # template = loader.get_template('railmate/index.html')  # templated version of the index page
    # return HttpResponse(template.render(request))
    return HttpResponse(render(request, 'railmate/index.html'))

def userpage(request, user_id):
    return HttpResponse("You're looking at user %s." % user_id)