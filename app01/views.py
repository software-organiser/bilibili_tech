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
    name = request.POST.get('name')
    date = catch_up.catch_up(bv,name).main()
    if date is not None:
        response = {"code":200,"success":True,"success_content":"数据获取处理成功","date":date}
    else:
        response = {"code":404,"success":False,"erroe_content":"数据获取处理失败"}
    return JsonResponse(response)
