from datetime import datetime
from zoneinfo import ZoneInfo
import json
import requests

from Masjid_Api import models


def schedule_api():
    all_country = models.Country_List.objects.all()
    playerID = []

    for country in all_country:
        all_fav_list = models.Favorite_Time_List.objects.filter(salat_Id__country=country)
        print(datetime.now(ZoneInfo(country.time_zone)).strftime('%H:%M') + ":00")
        for list in all_fav_list:
            isMatch = False
            if list.salat_Id.Fajr == datetime.now(ZoneInfo(country.time_zone)).strftime('%H:%M'):
                print(list.salat_Id.Fajr)
                print(list.user_id.onesignal_id)
                isMatch = True

            elif list.salat_Id.Dhuhr == datetime.now(ZoneInfo(country.time_zone)).strftime('%H:%M'):
                print(list.salat_Id.Dhuhr)
                print(list.user_id.onesignal_id)
                isMatch = True

            elif list.salat_Id.Asr == datetime.now(ZoneInfo(country.time_zone)).strftime('%H:%M'):
                print(list.salat_Id.Asr)
                print(list.user_id.onesignal_id)
                isMatch = True

            elif list.salat_Id.Maghrib == datetime.now(ZoneInfo(country.time_zone)).strftime('%H:%M'):
                print(list.salat_Id.Maghrib)
                print(list.user_id.onesignal_id)
                isMatch = True

            elif list.salat_Id.Isha == datetime.now(ZoneInfo(country.time_zone)).strftime('%H:%M'):
                print(list.salat_Id.Isha)
                print(list.user_id.onesignal_id)
                isMatch = True

            if isMatch:
                if list.user_id.onesignal_id not in playerID:
                    if list.user_id.onesignal_id != "":
                        playerID.append(list.user_id.onesignal_id)

    if len(playerID) != 0:
        # print(playerID)
        print(len(playerID))

        header = {"Content-Type": "application/json; charset=utf-8"}

        payload = {"app_id": "57490d06-e3e5-4095-ae60-0221224109b4",
                   "include_player_ids": playerID,
                   "contents": {"en": "Go to the salat",
                                "ru": "Lorem ipsum dolor amit"},
                   "data": {"body": "Hello my friend! we added a new post!", "title": "New post", },
                   "headings": {"en": "Salat Time Starting"}}

        req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))