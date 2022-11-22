# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
# Create your models here.
from MasjidApp import settings


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('User must have an username')

        user = self.model(email=self.normalize_email(email), username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email=self.normalize_email(email), password=password, username=username)

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User_model(AbstractBaseUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    phone = models.CharField(max_length=20, unique=True, null=True)
    address = models.TextField(max_length=300, null=True)
    is_creator = models.BooleanField(default=False)
    is_verification = models.BooleanField(default=False)
    create_at = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    update_at = models.DateTimeField(verbose_name='last login', auto_now=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    image = models.ImageField(upload_to='image/user_pic/%y/%m/%d', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    object = MyAccountManager()

    def delete(self, *args, **kwargs):
        # first, delete the file
        self.image.delete(save=False)

        # now, delete the object
        super(User_model, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        try:
            this = User_model.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete()
        except:
            pass
        super(User_model, self).save(*args, **kwargs)

    def __str__(self):
        return self.email

    def has_module_perms(self, app_label):
        return self.is_superuser

    def has_perm(self, perm, obj=None):
        return self.is_superuser


class Salat_Time_List(models.Model):
    mosque_name = models.CharField(max_length=200)
    mosque_icon = models.ImageField(null=True)
    user_id = models.ForeignKey(User_model, on_delete=models.CASCADE, limit_choices_to={'is_creator': True},
                                related_name="Salat_time")
    Fajr = models.TimeField(auto_created=False, blank=False, null=False)
    Sunrise = models.TimeField(auto_created=False, blank=True, null=True)
    Dhuhr = models.TimeField(auto_created=False, blank=False, null=False)
    Asr = models.TimeField(auto_created=False, blank=False, null=False)
    Sunset = models.TimeField(auto_created=False, blank=True, null=True)
    Maghrib = models.TimeField(auto_created=False, blank=False, null=False)
    Isha = models.TimeField(auto_created=False, blank=False, null=False)
    Imsak = models.TimeField(auto_created=False, blank=True, null=True)
    create_at = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    update_at = models.DateTimeField(verbose_name='last updated', auto_now=True, null=True)
    latitude = models.DecimalField(max_digits=15, decimal_places=10)
    longitude = models.DecimalField(max_digits=15, decimal_places=10)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    location = PointField(blank=True, null=True, srid=4326)
    def __str__(self):
        return self.mosque_name

    def save(self, *args, **kwargs):
        try:
            this = Salat_Time_List.objects.get(id=self.id)
            if this.image != self.mosque_icon:
                this.image.delete()
        except:
            pass

        try:
            self.location = Point(self.longitude, self.latitude)
            super(Salat_Time_List, self).save(*args, **kwargs)
        except Exception as e:
            pass

        super(Salat_Time_List, self).save(*args, **kwargs)


class Favorite_Time_List(models.Model):
    salat_Id = models.ForeignKey(Salat_Time_List, on_delete=models.CASCADE,
                                related_name="Salat_id")
    user_id = models.ForeignKey(User_model, on_delete=models.CASCADE,
                                related_name="user_id")
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.salat_Id.mosque_name
