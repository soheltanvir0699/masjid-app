from django.contrib import admin

# Register your models here.
from Masjid_Api.models import User_model, Salat_Time_List,Favorite_Time_List
# Register your models here.

admin.site.register(User_model)
admin.site.register(Salat_Time_List)
admin.site.register(Favorite_Time_List)