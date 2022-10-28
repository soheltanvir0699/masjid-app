import json
import urllib

import requests
from django.shortcuts import render
from ipware import get_client_ip
from datetime import datetime


def about(request):
    if request.method == 'GET':
        client_ip, is_routable = get_client_ip(request)

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return render(request, 'about.html',{"data": 0})


def blog(request):
    if request.method == 'GET':
        return render(request, 'blog.html',{})


def contact(request):
    if request.method == 'GET':
        return render(request, 'contact.html',{})


def download(request):
    if request.method == 'GET':
        return render(request, 'download.html',{})


def gallery(request):
    if request.method == 'GET':
       return render(request, 'gallery.html',{})


def index(request):
    if request.method == 'GET':
        client_ip, is_routable = get_client_ip(request)

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        url = f'https://api.ipfind.com/?ip={client_ip}'
        r = requests.get(url)
        r_status = r.status_code
        # print(r.json()["country"])
        city = r.json()["city"]
        country = r.json()["country"]
        url2 = "http://api.aladhan.com/v1/timingsByCity?city=" + f"{city}" + "&country=" + f"{country}" + "&method=2"
        data = requests.get(url2)
        print(data.json()["data"]["timings"])
        salatTime = data.json()["data"]["timings"]
        current_month_text = datetime.now().strftime('%h')
        current_day = datetime.now().strftime('%d')
        print(current_day, current_month_text)
        return render(request, 'index.html',
                      {"salatTime": salatTime, "current_day": current_day, "current_month": current_month_text})
