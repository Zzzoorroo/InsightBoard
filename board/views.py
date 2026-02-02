from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Welcome to InsightBoard</h1><p>The rocket has landed safely.</p>")