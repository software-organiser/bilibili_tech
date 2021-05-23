import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from app01 import catch_up,final_score
def index(request):
    return render(request, 'index.html')
@csrf_exempt
def catch_method(request):
    bv = request.POST.get('BV')
    name = request.POST.get('name')
    date = catch_up.catch_up(bv,name).main()
    pan = 0
    for i in date[3:]:
        if i ==0 or i is None:
            pan = 1
            break
        else:
            pan = 0
            continue
    if pan ==0:
        final = final_score.weight_model(date[3:])
        date.append(final)
        response = {"code": 200, "success": True, "success_content": "数据获取处理成功", "date": date}
    else:
        response = {"code": 404, "success": False, "error_content": "数据中含有为零或错误参数无法得出总分", "date": date}
    return JsonResponse(response)
