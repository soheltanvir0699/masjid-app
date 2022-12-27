from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import HttpResponse, JsonResponse, response
from urllib.parse import urlparse, parse_qs
from itertools import chain
from django.db.models import Q
from django.shortcuts import render
from datetime import datetime
import json
from django.contrib import messages, auth
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .tokens import account_activation_token
from django.core.mail import send_mail
from rest_framework import status
from django.urls import reverse
from django.core.mail import EmailMessage
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import User_model, Salat_Time_List, Favorite_Time_List, Country_List, update_Salat_Time_List
from .serializers import LoginSerializer, SingleUserSerializer, UserSerializer, Salat_Times_Serializer, Fav_Serializer, \
    Sch_Time_Serializer
import requests
import time
from ipware import get_client_ip
from .jobs import updater


# Create your views here.

class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        try:
            user = User_model.object.get(email=request.data['username'])
            print(user)
            invalidate_token = Token.objects.filter(user=user)
            print(invalidate_token)
            invalidate_token.delete()
            if user.is_active == False:
                return JsonResponse({"success": False, "message": 'Please check your email to verify your account..'})
        except:
            print('token not found')

        serializer = self.serializer_class(data=request.data)
        print(serializer)
        if serializer.is_valid():

            try:
                # auth.authenticate(username=serializer.data['username'], password=serializer.data['password'])
                user = User_model.object.get(email=serializer.data['username'])

                try:
                    user.onesignal_id = request.data['user_id']
                    user.save()
                except:
                    print()

                token = Token.objects.create(user=user)
                response = {}
                response['success'] = True
                response['message'] = "sing in successful."
                response['user'] = SingleUserSerializer(user, context={'request': request}).data
                response['token'] = token.key
            except:
                response = {}
                response['success'] = False

            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_auth(request):
    serialized = UserSerializer(data=request.data)
    if User_model.object.filter(email=request.data['email']).exists():
        return JsonResponse({"success": False, "message": 'your email is already use'})
    if serialized.is_valid():
        create_user = User_model.object.create(name=serialized.data['name'],
                                               email=serialized.data['email'],
                                               username=serialized.data['username'],
                                               password=make_password(serialized.data['password']),
                                               is_active=False,
                                               is_creator=serialized.data['is_creator'], image=request.data["image"])
        current_site = get_current_site(request)
        mail_subject = 'Confirm your email address'
        message = render_to_string('email_template.html', {
            'user': create_user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(create_user.pk)),
            'token': account_activation_token.make_token(create_user),
        })
        try:
            send_mail(mail_subject, message, 'Masjid App<masjidapp@aniyanetworks.net>', [request.data['email']])
        except:
            print("not send")

        print('password action')
        response = {}
        response['success'] = True
        response['message'] = "Please check your email to verify your account.."
        response['data'] = serialized.data
        return Response(response, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class requestpasswordresetemail(APIView):
    def get(self, request):
        return JsonResponse({"success": True})

    def post(self, request):
        email = request.data['email'].lower()
        print(email)
        # context = {
        #     'values': request.POST
        # }

        # if not validate_email(email):

        current_site = get_current_site(request)
        try:
            User = User_model.object.filter(email=email)
            if len(User) == 0:
                return JsonResponse({"success": False, "message": "Email not Valid."})
        except:
            return JsonResponse({"success": False, "message": "Email not Valid."})
        if User.exists():
            messages.success(request, 'We send an email')
            email_contents = {
                'user': User[0],
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(User[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(User[0]),
            }

            link = reverse('Api_View:compleat', kwargs={
                'uidb64': email_contents['uid'], 'token': email_contents['token']})

            email_subject = 'Reset your password'

            rest_url = 'https://masjidappword.herokuapp.com' + link

            email2 = EmailMessage(
                email_subject,
                'Hi there, Please use the link below to reset your password \n' + rest_url,
                "Masjid App<masjidapp@aniyanetworks.net>"
                ,
                [email],
            )
            try:
                ese = email2.send(fail_silently=True)
                messages.success(request, 'please check your email')
            except:
                messages.error(request, 'pleased enter a valid email')

        return JsonResponse({"success": True, "message": "Password reset email sent."})


def completepassword(request, uidb64, token):
    if request.method == "GET":
        context = {
            'uidb64': uidb64,
            'token': token
        }
        print(context)
        return render(request, 'set-rest-password.html', context)
    else:
        is_success = 0
        trashOldMsg(request)
        context = {'uidb64': uidb64, 'token': token, 'is_success': 0}
        password = request.POST['password']
        password2 = request.POST['password2']
        print(context, password2, password)
        if password != password2:
            trashOldMsg(request)
            messages.error(request, 'Passwords do not match')
            return render(request, 'set-rest-password.html', context)
        if len(password) < 6:
            trashOldMsg(request)
            messages.error(request, 'Password is too short')
            return render(request, 'set-rest-password.html', context)
        user_id = force_str(urlsafe_base64_decode(uidb64))
        print(user_id)
        user = User_model.object.get(pk=user_id)
        print(user)
        user.password = make_password(password)
        user.save()
        is_success = 1
        context['is_success'] = is_success
        messages.success(request, 'Password reset successful.')
        return render(request, 'success_temp.html', context)


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        try:
            token = request.META['HTTP_AUTHORIZATION'].split(" ")[1]
            print(token)
            invalidate_token = Token.objects.filter(key=token, user=request.user)
            invalidate_token.delete()
            return Response({"success": True, "message": "Logged out"}, status=status.HTTP_202_ACCEPTED)
        # Token shfajshaifsiue548747382dfsihfs87e8wfshfw8e7wisfhicsh8r8r7.split(" ")

        except:
            return Response({"success": False, "message": "Token does not exist!"}, status=status.HTTP_400_BAD_REQUEST)


class RemoveWithSalatToFavView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        try:
            salat_Id = request.data["salat_Id"]
        except:
            return Response({"success": False, "message": "Salat id Not found"})
        try:
            salat_data = Salat_Time_List.objects.get(id=salat_Id)
        except:
            return Response({"success": False, "message": "Salat Object Not found"})
        try:
            fav_data = Favorite_Time_List.objects.get(user_id=request.user, salat_Id=salat_data)
            fav_data.delete()
            return Response({"success": True, "message": "Remove to Favorite successful"},
                            status=status.HTTP_202_ACCEPTED)
        except:
            return Response({"success": False, "message": "Remove to Favorite Unsuccessful"},
                            status=status.HTTP_202_ACCEPTED)


class RemoveMasjidView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        try:
            salat_Id = request.data["salat_Id"]
        except:
            return Response({"success": False, "message": "Masjid id Not found"})
        try:
            salat_data = Salat_Time_List.objects.get(id=salat_Id)
            salat_data.delete()
            return Response({"success": True, "message": "Remove Masjid successful"},
                            status=status.HTTP_200_OK)
        except:
            return Response({"success": False, "message": "Masjid Object Not found"})


def trashOldMsg(req):
    storage = messages.get_messages(req)
    storage.user = True
    for _ in storage:
        pass
    for _ in list(storage._loaded_messages):
        del storage._loaded_messages[0]


class RemoveWithFavToFavView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        try:
            fav_id = request.data["fav_id"]
        except:
            return Response({"success": False, "message": "Favorite id Not found"})

        try:
            fav_data = Favorite_Time_List.objects.get(id=fav_id)
            fav_data.delete()
            return Response({"success": True, "message": "Remove to Favorite successful"},
                            status=status.HTTP_202_ACCEPTED)
        except:
            return Response({"success": False, "message": "Remove to Favorite Unsuccessful"},
                            status=status.HTTP_202_ACCEPTED)


class AddToFavView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        try:
            salat_Id = request.data["salat_Id"]
        except:
            return Response({"success": False, "message": "Salat id Not found"})
        try:
            is_fav = request.data["is_default"]
        except:
            is_fav = "False"

        if is_fav == "False":
            is_fav = False
        else:
            is_fav = True

        try:
            salat_data = Salat_Time_List.objects.get(id=salat_Id)
        except:
            return Response({"success": False, "message": "Salat Object Not found"})
        if is_fav != False:
            all_default_list = Favorite_Time_List.objects.filter(user_id=request.user, is_default=True)
            for data in all_default_list:
                data.is_default = False
                data.save()

        try:
            Fav_Data = Favorite_Time_List.objects.get(salat_Id=salat_data, user_id=request.user)
            Fav_Data.is_default = is_fav
            Fav_Data.save()
        except:
            Fav_Data = Favorite_Time_List.objects.create(salat_Id=salat_data, user_id=request.user, is_default=is_fav)
        try:
            Fav_Data_fav = Favorite_Time_List.objects.filter(user_id=request.user, is_default=True)
            if len(Fav_Data_fav) == 0:
                try:
                    Fav_Data.is_default = True
                    Fav_Data.save()
                except:
                    print("")
        except:
            print("")
        try:
            ser = Fav_Serializer(Fav_Data, context={'request': request}, many=False)
            return Response({"success": True, "message": "Added to Favorite successful", "data": ser.data},
                            status=status.HTTP_202_ACCEPTED)

        except:
            return Response({"success": False, "message": "Added to Favorite unsuccessful"})

    def get(self, request, **kwargs):

        try:
            fav_list = Favorite_Time_List.objects.filter(user_id=request.user).distinct()
            ser = Fav_Serializer(fav_list, context={'request': request}, many=True)
            return Response({"success": True, "message": "get data successful", "data": ser.data},
                            status=status.HTTP_202_ACCEPTED)

        except:
            return Response({"success": False, "message": "get data unsuccessful"})


class All_Masjid_View(APIView):

    def post(self, request, **kwargs):
        try:
            email = request.data['email'].lower()
        except:
            email = ""
        try:
            state = request.data['state'].upper()
        except:
            state = ""
        try:
            city = request.data['city'].upper()
        except:
            city = ""
        try:
            country = request.data['country'].upper()
        except:
            country = ""

        try:
            masjid_by_state = Salat_Time_List.objects.filter(state=state)
            masjid_by_city = Salat_Time_List.objects.filter(city=city).filter(~Q(state=state))
            masjid_by_country = Salat_Time_List.objects.filter(country=country).filter(~Q(state=state)).filter(
                ~Q(city=city))
            # if state != "":
            #
            # else:
            #     masjid_by_state = None
            # if city != "":
            #
            # else:
            #     masjid_by_city = None
            # if country != "":
            #
            # else:
            #     masjid_by_country = None
            masjid = Salat_Time_List.objects.filter(~Q(country=country)).filter(~Q(city=city)).filter(~Q(state=state))
            combined_results = masjid_by_state | masjid_by_city | masjid_by_country | masjid
            paginator = PageNumberPagination()
            paginator.page_size = 15
            result_page = paginator.paginate_queryset(combined_results, request)
            serializer = Salat_Times_Serializer(result_page, context={'request': request, 'email': email},
                                                many=True)
            return Response({"success": True, "message": "Data get successful.",
                             "data": paginator.get_paginated_response(serializer.data).data},
                            status=status.HTTP_202_ACCEPTED)

        except:
            return Response({"success": False, "message": "Data get unsuccessful."})


class Search_Masjid_View(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        try:
            email = request.data['email'].lower()
        except:
            email = ""

        try:
            keyword = request.GET.get('keyword', '!!!!')
            print(keyword)
            masjid = Salat_Time_List.objects.filter(Q(mosque_name__icontains=keyword)) | Salat_Time_List.objects.filter(
                Q(address__icontains=keyword))
            paginator = PageNumberPagination()
            paginator.page_size = 15
            result_page = paginator.paginate_queryset(masjid, request)
            serializer = Salat_Times_Serializer(masjid, context={'request': request, 'email': email}, many=True)
            print(masjid)
            return Response({"success": True, "message": "Data get successful.",
                             "data": paginator.get_paginated_response(serializer.data).data},
                            status=status.HTTP_202_ACCEPTED)
        # Token shfajshaifsiue548747382dfsihfs87e8wfshfw8e7wisfhicsh8r8r7.split(" ")

        except:
            return Response({"success": False, "message": "Data get unsuccessful."})


class update_masjid(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        print(request.user.id)
        try:
            id = request.data['id']
        except:
            return Response({"success": False, "message": "Id is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            fajr_date = request.data['Fajr']
        except:
            return Response({"success": False, "message": "Fajr time is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            dhuhr_date = request.data['Dhuhr']
        except:
            return Response({"success": False, "message": "Dhuhr time is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            asr_date = request.data['Asr']
        except:
            return Response({"success": False, "message": "Asr time is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            maghrib_date = request.data['Maghrib']
        except:
            return Response({"success": False, "message": "Maghrib time is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            isha_date = request.data['Isha']
        except:
            return Response({"success": False, "message": "Isha time is empty."}, status=status.HTTP_202_ACCEPTED)

        try:
            mosque_name = request.data['mosque_name']
        except:
            return Response({"success": False, "message": "Mosque name is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            mosque_icon = request.data['mosque_icon']
        except:
            mosque_icon = None

        try:
            state = request.data['state'].upper()
        except:
            return Response({"success": False, "message": "State name is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            city = request.data['city'].upper()
        except:
            return Response({"success": False, "message": "City name is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            country = request.data['country'].upper()
        except:
            return Response({"success": False, "message": "Country name is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            current_masjid = Salat_Time_List.objects.get(id=id)
        except:
            return Response({"success": False, "message": "Masjid Not Found."}, status=status.HTTP_202_ACCEPTED)

        try:
            current_masjid.mosque_name = mosque_name
            current_masjid.mosque_icon = mosque_icon
            current_masjid.Fajr = fajr_date
            current_masjid.Dhuhr = dhuhr_date
            current_masjid.Asr = asr_date
            current_masjid.Maghrib = maghrib_date
            current_masjid.Isha = isha_date
            current_masjid.state = state
            current_masjid.city = city
            current_masjid.country = country
            current_masjid.save()
            try:
                subs_users = Favorite_Time_List.objects.filter(salat_Id=current_masjid)
                userId = []
                for user in subs_users:
                    if user.user_id.onesignal_id not in userId:
                        if user.user_id.onesignal_id != "":
                            userId.append(user.user_id.onesignal_id)
                header = {"Content-Type": "application/json; charset=utf-8"}

                payload = {"app_id": "57490d06-e3e5-4095-ae60-0221224109b4",
                           "include_player_ids": userId,
                           "contents": {"en": current_masjid.mosque_name + " time is now updated.",
                                        "ru": "Lorem ipsum dolor amit"},
                           "data": {"body": "Hello my friend! we added a new post!", "title": "New post", },
                           "headings": {"en": "Your salat time Changed." }}

                req = requests.post("https://onesignal.com/api/v1/notifications", headers=header,
                                    data=json.dumps(payload))
            except:
                print()
            serializer_data = Salat_Times_Serializer(current_masjid, context={'request': request}, many=False)
            return Response({"success": True, "message": "Successful date save.", "data": serializer_data.data},
                            status=status.HTTP_202_ACCEPTED)
        except:
            return Response({"success": False, "message": "Unsuccessful date save."},
                            status=status.HTTP_200_OK)


class delete_masjid_date_list(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        print(request.user.id)
        try:
            id = request.data['id']
        except:
            return Response({"success": False, "message": "Id is empty."}, status=status.HTTP_202_ACCEPTED)

        try:
            Sch_Data = update_Salat_Time_List.objects.get(id=id)
            Sch_Data.delete()
            return Response({"success": True, "message": "Successful data delete."},
                            status=status.HTTP_202_ACCEPTED)
        except:
            return Response({"success": False, "message": "Unsuccessful data delete."},
                            status=status.HTTP_202_ACCEPTED)


class update_masjid_date_list(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        print(request.user.id)
        try:
            name = request.data['name']
        except:
            return Response({"success": False, "message": "Name is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            date = request.data['date']
        except:
            return Response({"success": False, "message": "Date is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            id = request.data['id']
        except:
            return Response({"success": False, "message": "Id is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            fajr_date = request.data['Fajr']
        except:
            return Response({"success": False, "message": "Fajr time is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            dhuhr_date = request.data['Dhuhr']
        except:
            return Response({"success": False, "message": "Dhuhr time is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            asr_date = request.data['Asr']
        except:
            return Response({"success": False, "message": "Asr time is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            maghrib_date = request.data['Maghrib']
        except:
            return Response({"success": False, "message": "Maghrib time is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            isha_date = request.data['Isha']
        except:
            return Response({"success": False, "message": "Isha time is empty."}, status=status.HTTP_202_ACCEPTED)

        try:
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            newdate1 = time.strptime(current_date, "%Y-%m-%d")
            newdate2 = time.strptime(date, "%Y-%m-%d")

            Sch_Data = update_Salat_Time_List.objects.get(id=id)
            Sch_Data.update_date = date
            Sch_Data.Dhuhr = dhuhr_date
            Sch_Data.name = name
            Sch_Data.Asr = asr_date
            Sch_Data.Isha = isha_date
            Sch_Data.Maghrib = maghrib_date
            Sch_Data.Fajr = fajr_date
            if newdate2 > newdate1:
                Sch_Data.is_expired = False
                print(current_date)
            else:
                Sch_Data.is_expired = True
            Sch_Data.save()
            return Response({"success": True, "message": "Successful date update."},
                            status=status.HTTP_202_ACCEPTED)
        except:
            return Response({"success": False, "message": "Unsuccessful date update."},
                            status=status.HTTP_202_ACCEPTED)


class create_masjid_date_list(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        print(request.user.id)
        try:
            date = request.data['date']
        except:
            return Response({"success": False, "message": "Date is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            name = request.data['name']
        except:
            return Response({"success": False, "message": "Name is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            fajr_date = request.data['Fajr']
        except:
            return Response({"success": False, "message": "Fajr time is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            dhuhr_date = request.data['Dhuhr']
        except:
            return Response({"success": False, "message": "Dhuhr time is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            asr_date = request.data['Asr']
        except:
            return Response({"success": False, "message": "Asr time is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            maghrib_date = request.data['Maghrib']
        except:
            return Response({"success": False, "message": "Maghrib time is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            isha_date = request.data['Isha']
        except:
            return Response({"success": False, "message": "Isha time is empty."}, status=status.HTTP_202_ACCEPTED)

        user = User_model.object.get(id=request.user.id)
        try:
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            newdate1 = time.strptime(current_date, "%Y-%m-%d")
            newdate2 = time.strptime(date, "%Y-%m-%d")
            if newdate2 > newdate1:
                print(current_date)
                update_Salat_Time_List.objects.create(name=name, user_id=user, update_date=date, Fajr=fajr_date, Dhuhr=dhuhr_date,
                                                      Asr=asr_date, Maghrib=maghrib_date, Isha=isha_date)
                return Response({"success": True, "message": "Successful date save."},
                                status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"success": False, "message": "Select Next days Date."},
                                status=status.HTTP_202_ACCEPTED)

        except:
            return Response({"success": False, "message": "Unsuccessful date save."},
                            status=status.HTTP_202_ACCEPTED)

    def get(self, request):
        user = User_model.object.get(id=request.user.id)
        try:
            nextSchList = update_Salat_Time_List.objects.filter(user_id=user)
            data = Sch_Time_Serializer(nextSchList, context={'request': request}, many=True)
            return Response({"success": True, "message": "Data get successful.", "data": data.data},
                            status=status.HTTP_202_ACCEPTED)
        except:
            print("")
            return Response({"success": False, "message": "Data get unsuccessful."}, status=status.HTTP_202_ACCEPTED)


import datetime


class startSch(APIView):
    def get(self, request):
        updater.start()
        return Response({"success": True, "message": "started sch."},
                        status=status.HTTP_202_ACCEPTED)


class TimeZone_Times(APIView):
    def get(self, request, **kwargs):
        try:
            user = User_model.object.get(id=request.user.id)
            client_ip, is_routable = get_client_ip(request)
            url = f'https://api.ipfind.com/?ip={client_ip}'
            # url = f'https://api.ipfind.com/?ip=116.204.228.142'
            r = requests.get(url)
            user.time_zone = r.json()["country"].lower()
            user.save()
            return Response(
                {"success": True, "time_zone": r.json()["timezone"].lower(), "country": r.json()["country"]},
                status=status.HTTP_202_ACCEPTED)
        except:
            client_ip, is_routable = get_client_ip(request)
            url = f'https://api.ipfind.com/?ip={client_ip}'
            # url = f'https://api.ipfind.com/?ip=116.204.228.142'
            r = requests.get(url)
            return Response(
                {"success": True, "time_zone": r.json()["timezone"].lower(), "country": r.json()["country"]},
                status=status.HTTP_202_ACCEPTED)


class Salat_Times(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        print(request.user.id)
        client_ip, is_routable = get_client_ip(request)

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        url = f'https://api.ipfind.com/?ip={client_ip}'
        # url = f'https://api.ipfind.com/?ip=116.204.228.142'
        r = requests.get(url)

        user = User_model.object.get(id=request.user.id)
        try:
            fajr_date = request.data['Fajr']
        except:
            return Response({"success": False, "message": "Fajr time is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            dhuhr_date = request.data['Dhuhr']
        except:
            return Response({"success": False, "message": "Dhuhr time is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            asr_date = request.data['Asr']
        except:
            return Response({"success": False, "message": "Asr time is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            maghrib_date = request.data['Maghrib']
        except:
            return Response({"success": False, "message": "Maghrib time is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            isha_date = request.data['Isha']
        except:
            return Response({"success": False, "message": "Isha time is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            Sunrise = request.data['Sunrise']
        except:
            Sunrise = None
        try:
            Sunset = request.data['Sunset']
        except:
            Sunset = None
        try:
            mosque_name = request.data['mosque_name']
        except:
            return Response({"success": False, "message": "Mosque name is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            mosque_icon = request.data['mosque_icon']
        except:
            mosque_icon = None
        try:
            state = request.data['state']
        except:
            return Response({"success": False, "message": "State name is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            city = request.data['city']
        except:
            return Response({"success": False, "message": "City name is empty."}, status=status.HTTP_202_ACCEPTED)
        try:
            country = request.data['country']
        except:
            return Response({"success": False, "message": "Country name is empty."}, status=status.HTTP_202_ACCEPTED)

        try:
            # timezone
            timezone = r.json()["timezone"]
            print(timezone)
            country_list = Country_List.objects.create(country_name=country.lower(), time_zone=timezone)
            country_list.save()
        except:
            print("")

        salatList = Salat_Time_List.objects.filter(user_id=user)
        if len(salatList) != 0:
            return Response({"success": False, "message": "Can't create more than one Masjid"},
                            status=status.HTTP_202_ACCEPTED)
        if country.lower() == r.json()["country"].lower():
            time_sa = Salat_Time_List.objects.create(mosque_name=mosque_name, mosque_icon=mosque_icon, user_id=user,
                                                     Fajr=fajr_date, Sunrise=Sunrise, Dhuhr=dhuhr_date, Asr=asr_date,
                                                     Sunset=Sunset, Maghrib=maghrib_date, Isha=isha_date, state=state,
                                                     city=city, country=country.lower())
            time_sa.save()
            serializer_data = Salat_Times_Serializer(time_sa, context={'request': request}, many=False)
            return Response({"success": True, "message": "Successful date save.", "data": serializer_data.data},
                            status=status.HTTP_202_ACCEPTED)
        else:
            return Response({"success": False, "message": "Masjid TimeZone not match with your TimeZone.", "data": []},
                            status=status.HTTP_202_ACCEPTED)

    def get(self, request, **kwargs):

        user = User_model.object.get(id=request.user.id)
        salatData = Salat_Time_List.objects.filter(user_id=user)
        serializer = Salat_Times_Serializer(salatData, context={'request': request}, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_202_ACCEPTED)


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.object.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'conformation_design.html')
    else:
        return render(request, 'conformation_design.html')


class send_push_notification(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        user = User_model.object.get(id=request.user.id)
        try:
            title = request.data['title']
        except:
            return Response({"success": False, "message": "Push Title is empty."}, status=status.HTTP_200_OK)
        try:
            descriptions = request.data['descriptions']
        except:
            return Response({"success": False, "message": "Push Descriptions is empty."},
                            status=status.HTTP_200_OK)
        my_masjid = Salat_Time_List.objects.get(user_id=user)
        try:
            subs_users = Favorite_Time_List.objects.filter(salat_Id=my_masjid)
            userId = ["b1e24206-4f29-42aa-bcd7-c354890b88b4"]
            for user in subs_users:
                if user.user_id.onesignal_id not in userId:
                    if user.user_id.onesignal_id != "":
                        userId.append(user.user_id.onesignal_id)
            header = {"Content-Type": "application/json; charset=utf-8"}

            payload = {"app_id": "57490d06-e3e5-4095-ae60-0221224109b4",
                       "include_player_ids": userId,
                       "contents": {"en": descriptions,
                                    "ru": "Lorem ipsum dolor amit"},
                       "data": {"body": "Hello my friend! we added a new post!", "title": "New post", },
                       "headings": {"en": title}}

            req = requests.post("https://onesignal.com/api/v1/notifications", headers=header,
                                data=json.dumps(payload))
            return Response({"success": True, "message": "Push Send Successful.","data":req.json()},
                            status=status.HTTP_200_OK)
        except:
            print()
        return Response({"success": True, "message": "Push Send Successful."},
                        status=status.HTTP_200_OK)
