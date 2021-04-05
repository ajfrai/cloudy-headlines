import os
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
import requests
from .models import Greeting

# Create your views here.
def index(request):
	STATIC_ROOT = os.path.join(settings.BASE_DIR, "hello/static")
	clouds = os.listdir(os.path.join(STATIC_ROOT,'clouds/1'))
	cloud_path = os.path.join('clouds/1',clouds[-1])
	return render(request, "cloud.html", {"cloud_path": cloud_path})

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, "db.html", {"greetings": greetings})
