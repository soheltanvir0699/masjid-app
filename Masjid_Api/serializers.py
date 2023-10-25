from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.db.models import Sum
from rest_framework import serializers
from .models import User_model, Salat_Time_List, Favorite_Time_List, update_Salat_Time_List


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get("username").lower()
        password = attrs.get("password")
        print(username, password)

        user = auth.authenticate(username=username, password=password)
        print(user, 'now user')
        if user:
            attrs["user"] = user
            return attrs
        else:
            raise serializers.ValidationError(
                "Unable to login with credentials provided."
            )


class SingleUserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField('get_image_url')

    class Meta:
        model = User_model
        fields = ('name', 'email', 'username', 'phone', 'address', 'image', 'is_creator',)

    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        else:
            return ""


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_model
        fields = ('username', 'password', 'email', 'name', 'is_creator')
        write_only_fields = ('password',)


class Salat_Times_Serializer(serializers.ModelSerializer):
    is_add_fav = serializers.SerializerMethodField()

    class Meta:
        model = Salat_Time_List
        fields = '__all__'

    def get_is_add_fav(self, obj):
        try:
            user = User_model.object.get(email=self.context['email'])
            subs = Favorite_Time_List.objects.get(salat_Id=obj, user_id=user)
            return True
        except:
            return False


class Sch_Time_Serializer(serializers.ModelSerializer):
    class Meta:
        model = update_Salat_Time_List
        fields = '__all__'


class Fav_Serializer(serializers.ModelSerializer):
    salat_Id = serializers.SerializerMethodField()

    class Meta:
        model = Favorite_Time_List
        fields = '__all__'

    def get_salat_Id(self, obj):
        data = Salat_Times_Serializer(Salat_Time_List.objects.filter(id=obj.salat_Id.id), context=self.context,
                                      many=True).data
        return data
