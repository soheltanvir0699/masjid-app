# Generated by Django 4.1.4 on 2022-12-26 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masjid_Api', '0003_user_model_time_zone'),
    ]

    operations = [
        migrations.AddField(
            model_name='update_salat_time_list',
            name='is_expired',
            field=models.BooleanField(default=False),
        ),
    ]