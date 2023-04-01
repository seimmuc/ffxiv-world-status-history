from django.http import HttpRequest
from django.shortcuts import render

# Create your views here.


def index(request: HttpRequest):
    return render(request=request, template_name='ffxivws/index.html', context={})
