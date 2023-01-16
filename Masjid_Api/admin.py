from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
# Register your models here.
from Masjid_Api.models import User_model, Salat_Time_List, Favorite_Time_List
from . import models


# Register your models here.


@admin.register(models.User_model)
class EmployeeAdmin(ImportExportModelAdmin):
    ordering = ('name',)
    search_fields = ['name', 'email']
    pass


@admin.register(models.Salat_Time_List)
class EmployeeAdmin(ImportExportModelAdmin):
    ordering = ('mosque_name',)
    search_fields = ['mosque_name', 'address']
    pass


@admin.register(models.Favorite_Time_List)
class EmployeeAdmin(ImportExportModelAdmin):
    pass

@admin.register(models.Country_List)
class EmployeeAdmin(ImportExportModelAdmin):
    pass

@admin.register(models.update_Salat_Time_List)
class EmployeeAdmin(ImportExportModelAdmin):
    pass
