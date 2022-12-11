import datetime
from zoneinfo import ZoneInfo
import json
import requests

from Masjid_Api import models


def schedule_api():
    print("working")
    all_country = models.Country_List.objects.all()
    playerID = []
    AsrplayerID = []
    FajrplayerID = []
    MagribplayerID = []
    DhuhrplayerID = []
    IshaplayerID = []

    for country in all_country:

        # print(datetime.datetime.now(ZoneInfo(country.time_zone)).strftime('%H:%M') + ":00")
        now = datetime.datetime.now(ZoneInfo(country.time_zone))
        now1 = datetime.datetime.now(ZoneInfo(country.time_zone)) - datetime.timedelta(minutes=1)
        current_time = now.strftime('%H:%M')
        current_time2 = now1.strftime('%H:%M')
        all_fav_list1 = models.Favorite_Time_List.objects.filter(salat_Id__country=country).filter(salat_Id__Fajr=current_time)
        all_fav_list2 = models.Favorite_Time_List.objects.filter(salat_Id__country=country).filter(
            salat_Id__Fajr=current_time2)

        all_fav_list3 = models.Favorite_Time_List.objects.filter(salat_Id__country=country).filter(
            salat_Id__Dhuhr=current_time)
        all_fav_list4 = models.Favorite_Time_List.objects.filter(salat_Id__country=country).filter(
            salat_Id__Dhuhr=current_time2)

        all_fav_list5 = models.Favorite_Time_List.objects.filter(salat_Id__country=country).filter(
            salat_Id__Asr=current_time)
        all_fav_list6 = models.Favorite_Time_List.objects.filter(salat_Id__country=country).filter(
            salat_Id__Asr=current_time2)

        all_fav_list7 = models.Favorite_Time_List.objects.filter(salat_Id__country=country).filter(
            salat_Id__Maghrib=current_time)
        all_fav_list8 = models.Favorite_Time_List.objects.filter(salat_Id__country=country).filter(
            salat_Id__Maghrib=current_time2)

        all_fav_list9 = models.Favorite_Time_List.objects.filter(salat_Id__country=country).filter(
            salat_Id__Isha=current_time)
        all_fav_list10 = models.Favorite_Time_List.objects.filter(salat_Id__country=country).filter(
            salat_Id__Isha=current_time2)
        all_fav_list = all_fav_list1 | all_fav_list2 | all_fav_list3 | all_fav_list4 | all_fav_list5 | all_fav_list6 | all_fav_list7 | all_fav_list8 | all_fav_list9 | all_fav_list10
        current_time = now.strftime('%H:%M') + ":00"
        current_time2 = now1.strftime('%H:%M') + ":00"

        for list in all_fav_list:
            if list.salat_Id.Fajr == current_time or list.salat_Id.Fajr ==current_time2:
                if list.user_id.onesignal_id not in FajrplayerID:
                    if list.user_id.onesignal_id != "":
                        FajrplayerID.append(list.user_id.onesignal_id)

            elif list.salat_Id.Dhuhr == current_time or list.salat_Id.Dhuhr == current_time2:
                if list.user_id.onesignal_id not in DhuhrplayerID:
                    if list.user_id.onesignal_id != "":
                        DhuhrplayerID.append(list.user_id.onesignal_id)

            elif list.salat_Id.Asr == current_time or list.salat_Id.Asr == current_time2:
                if list.user_id.onesignal_id not in AsrplayerID:
                    if list.user_id.onesignal_id != "":
                        AsrplayerID.append(list.user_id.onesignal_id)

            elif list.salat_Id.Maghrib == current_time or list.salat_Id.Maghrib == current_time2:
                if list.user_id.onesignal_id not in MagribplayerID:
                    if list.user_id.onesignal_id != "":
                        MagribplayerID.append(list.user_id.onesignal_id)

            elif list.salat_Id.Isha == current_time or list.salat_Id.Isha == current_time2:
                if list.user_id.onesignal_id not in IshaplayerID:
                    if list.user_id.onesignal_id != "":
                        IshaplayerID.append(list.user_id.onesignal_id)
            #
            # if isMatch:
            #     if list.user_id.onesignal_id not in playerID:
            #         if list.user_id.onesignal_id != "":
            #             playerID.append(list.user_id.onesignal_id)

    if len(playerID) != 0:
        # print(playerID)
        print(len(playerID))

        header = {"Content-Type": "application/json; charset=utf-8"}

        payload = {"app_id": "57490d06-e3e5-4095-ae60-0221224109b4",
                   "include_player_ids": FajrplayerID,
                   "contents": {"en": "Salat Start",
                                "ru": "Lorem ipsum dolor amit"},
                   "data": {"body": "Hello my friend! we added a new post!", "title": "New post", },
                   "headings": {"en": "Fajr"}}
        payloadAsr = {"app_id": "57490d06-e3e5-4095-ae60-0221224109b4",
                   "include_player_ids": AsrplayerID,
                   "contents": {"en": "Salat Start",
                                "ru": "Lorem ipsum dolor amit"},
                   "data": {"body": "Hello my friend! we added a new post!", "title": "New post", },
                   "headings": {"en": "Asr"}}
        payloadMaghrib = {"app_id": "57490d06-e3e5-4095-ae60-0221224109b4",
                      "include_player_ids": MagribplayerID,
                      "contents": {"en": "Salat Start",
                                   "ru": "Lorem ipsum dolor amit"},
                      "data": {"body": "Hello my friend! we added a new post!", "title": "New post", },
                      "headings": {"en": "Maghrib"}}
        payloadDhuhr = {"app_id": "57490d06-e3e5-4095-ae60-0221224109b4",
                      "include_player_ids": DhuhrplayerID,
                      "contents": {"en": "Salat Start",
                                   "ru": "Lorem ipsum dolor amit"},
                      "data": {"body": "Hello my friend! we added a new post!", "title": "New post", },
                      "headings": {"en": "Dhuhr"}}
        payloadIsha = {"app_id": "57490d06-e3e5-4095-ae60-0221224109b4",
                      "include_player_ids": IshaplayerID,
                      "contents": {"en": "Salat Start",
                                   "ru": "Lorem ipsum dolor amit"},
                      "data": {"body": "Hello my friend! we added a new post!", "title": "New post", },
                      "headings": {"en": "Isha"}}

        req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
        req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payloadIsha))
        req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payloadDhuhr))
        req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payloadMaghrib))
        req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payloadAsr))