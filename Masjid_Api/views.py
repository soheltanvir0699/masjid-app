from django.contrib import auth
from django.core.mail import send_mail
from django.db.models import Sum, Avg, Max, Min
from django.http import HttpResponse, JsonResponse, response
from urllib.parse import urlparse, parse_qs
from django.db.models import Q
from django.shortcuts import render
from datetime import datetime
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .tokens import account_activation_token
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import User_model, Salat_Time_List, Favorite_Time_List
from .serializers import LoginSerializer, SingleUserSerializer, UserSerializer, Salat_Times_Serializer, Fav_Serializer


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
            if not user.is_active:
                return JsonResponse({"success": False, "message": 'Please check your email to verify your account..'})
        except:
            print('token not found')

        serializer = self.serializer_class(data=request.data)
        print(serializer)
        if serializer.is_valid():

            try:
                # auth.authenticate(username=serializer.data['username'], password=serializer.data['password'])
                user = User_model.object.get(email=serializer.data['username'])
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
            masjid = Salat_Time_List.objects.all()
            serializer = Salat_Times_Serializer(masjid, context={'request': request, 'email': email}, many=True)
            print(masjid)
            return Response({"success": True, "message": "Data get successful.", "data": serializer.data},
                            status=status.HTTP_202_ACCEPTED)
        # Token shfajshaifsiue548747382dfsihfs87e8wfshfw8e7wisfhicsh8r8r7.split(" ")

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
            masjid = Salat_Time_List.objects.filter(Q(mosque_name__icontains=keyword))
            serializer = Salat_Times_Serializer(masjid, context={'request': request, 'email': email}, many=True)
            print(masjid)
            return Response({"success": True, "message": "Data get successful.", "data": serializer.data},
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
            current_masjid = Salat_Time_List.objects.get(id=id)
        except:
            return Response({"success": False, "message": "Masjid Not Found."}, status=status.HTTP_202_ACCEPTED)
        current_masjid.mosque_name = mosque_name
        current_masjid.mosque_icon = mosque_icon
        current_masjid.Fajr = fajr_date
        current_masjid.Dhuhr = dhuhr_date
        current_masjid.Asr = asr_date
        current_masjid.Maghrib = maghrib_date
        current_masjid.Isha = isha_date
        current_masjid.save()
        serializer_data = Salat_Times_Serializer(current_masjid, context={'request': request}, many=False)
        return Response({"success": True, "message": "Successful date save.", "data": serializer_data.data},
                        status=status.HTTP_202_ACCEPTED)


class Salat_Times(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        print(request.user.id)
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

        time_sa = Salat_Time_List.objects.create(mosque_name=mosque_name, mosque_icon=mosque_icon, user_id=user,
                                                 Fajr=fajr_date, Sunrise=Sunrise, Dhuhr=dhuhr_date, Asr=asr_date,
                                                 Sunset=Sunset, Maghrib=maghrib_date, Isha=isha_date)
        time_sa.save()
        serializer_data = Salat_Times_Serializer(time_sa, context={'request': request}, many=False)
        return Response({"success": True, "message": "Successful date save.", "data": serializer_data.data},
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
