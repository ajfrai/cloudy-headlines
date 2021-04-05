import os
from django.shortcuts import render
from django.http import HttpResponse
import requests
from .models import Greeting

# Create your views here.
def index(request):
	clouds = os.listdir('clouds/1')
	cloud_path = clouds[-1]
    render(request, "cloud.html", {"cloud_path": cloud_path})

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, "db.html", {"greetings": greetings})
