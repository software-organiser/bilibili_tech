import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from app01 import catch_up
def index(request):
    return render(request, 'index.html')
@csrf_exempt
def catch_method(request):
    bv = request.POST.get('BV')
    d = catch_up.catch_up(bv).main2()
    return JsonResponse(d)
