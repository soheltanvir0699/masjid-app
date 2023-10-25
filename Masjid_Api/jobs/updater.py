from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import schedule_api,updateMasjid


def start():
    scheduler = BackgroundScheduler()
    scheduler.remove_all_jobs()
    scheduler.add_job(schedule_api, 'interval', minutes=2)
    scheduler.add_job(updateMasjid, 'interval', hours=24)
    scheduler.start()
