import datetime
from zoneinfo import ZoneInfo
import json
import requests

from Masjid_Api import models


def updateMasjid():
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    current_updated_date = models.update_Salat_Time_List.objects.filter(update_date=current_date)
    if len(current_updated_date) != 0:
        for data in current_updated_date:
            current_user = models.User_model.objects.get(id=data.user_id.id)
            salat_list_data = models.Salat_Time_List.objects.get(user_id=current_user)
            try:
                salat_list_data.Fajr = data.Fajr
                salat_list_data.Isha = data.Isha
                salat_list_data.Maghrib = data.Maghrib
                salat_list_data.Asr = data.Asr
                salat_list_data.Dhuhr = data.Dhuhr
                salat_list_data.save()
                data.delete()
            except:
                print("")


            subs_users = models.Favorite_Time_List.objects.filter(salat_Id=salat_list_data)
            userId = []
            masjid_name = ""
            for user in subs_users:
                if masjid_name != "":
                    masjid_name = user.salat_Id.mosque_name
                if user.user_id.onesignal_id not in userId:
                    if user.user_id.onesignal_id != "":
                        userId.append(user.user_id.onesignal_id)
            header = {"Content-Type": "application/json; charset=utf-8"}

            payload = {"app_id": "57490d06-e3e5-4095-ae60-0221224109b4",
                       "include_player_ids": userId,
                       "contents": {"en": "Your salat time Changed.",
                                    "ru": "Lorem ipsum dolor amit"},
                       "data": {"body": "Hello my friend! we added a new post!", "title": "New post", },
                       "headings": {"en": masjid_name + " time is now updated."}}

            req = requests.post("https://onesignal.com/api/v1/notifications", headers=header,
                                data=json.dumps(payload))


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
        all_fav_list1 = models.Favorite_Time_List.objects.filter(salat_Id__country=country).filter(
            salat_Id__Fajr=current_time)
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
            if list.salat_Id.Fajr == current_time or list.salat_Id.Fajr == current_time2:
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

    if len(FajrplayerID) != 0:
        req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
    if len(AsrplayerID) != 0:
        req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payloadAsr))

    if len(MagribplayerID) != 0:
        req = requests.post("https://onesignal.com/api/v1/notifications", headers=header,
                            data=json.dumps(payloadMaghrib))

    if len(DhuhrplayerID) != 0:
        req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payloadDhuhr))

    if len(IshaplayerID) != 0:
        req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payloadIsha))
