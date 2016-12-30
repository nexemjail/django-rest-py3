from django.shortcuts import render
from django.http import response

# Create your views here.


def v(request):
    # print 55555
    return response.HttpResponse(content='<h1>It works!</h1>')