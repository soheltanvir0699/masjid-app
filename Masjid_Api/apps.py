from django.apps import AppConfig
import os

class MasjidApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Masjid_Api'

    def ready(self):
        from .jobs import updater
        # updater.start()
        if (os.environ.get("DYNO")):
            updater.start()


