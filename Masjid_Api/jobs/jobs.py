from django.conf import settings
import requests
import json
import random
from Masjid_Api import models


def schedule_api():
   all_country = models.Country_List.objects.all()
   print(all_country)
   for country in all_country:
       all_fav_list = models.Favorite_Time_List.objects.filter(salat_Id__country=country)