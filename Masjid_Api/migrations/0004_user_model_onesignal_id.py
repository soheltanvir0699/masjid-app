# Generated by Django 3.2 on 2022-12-02 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masjid_Api', '0003_alter_salat_time_list_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_model',
            name='onesignal_id',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
