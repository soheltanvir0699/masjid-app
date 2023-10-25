import json
import urllib
# from geopy import distance
import requests
from django.shortcuts import render
from ipware import get_client_ip
from datetime import datetime
from .models import Salat_Time_List


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

# def get_distance(user_co, friend_co):
#     coords_1 = (user_co.get('lat'), user_co.get('long'))
#     coords_2 = (float(friend_co.get('lat')), float(friend_co.get('long')))
#
#     return distance.distance(coords_1, coords_2).km

def index(request):

    if request.method == 'GET':

        # user = {'lat': 25.276987, 'long': 55.296249}
        # friends = {'user2': {'lat': '25.122212', 'long': '55.296249'},
        #            'user3': {'lat': '25.222212', 'long': '55.396249'}}
        #
        # for key, value in friends.items():
        #     dstnce = get_distance(user, value)
        #     print(value,dstnce)
        #     if dstnce < 50:
        #         print("Friend {} is in 50 KM".format(key))
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

def nearby_spots_old(request, lat, lng, radius=5000, limit=50):
    """
    WITHOUT use of any external library, using raw MySQL and Haversine Formula
    http://en.wikipedia.org/wiki/Haversine_formula
    """
    radius = float(radius) / 1000.0

    query = """SELECT id, (6367*acos(cos(radians(%2f))
               *cos(radians(latitude))*cos(radians(longitude)-radians(%2f))
               +sin(radians(%2f))*sin(radians(latitude))))
               AS distance FROM demo_spot HAVING
               distance < %2f ORDER BY distance LIMIT 0, %d""" % (
        float(lat),
        float(lng),
        float(lat),
        radius,
        limit
    )

    # queryset = Spot.objects.raw(query)
    # print(queryset)