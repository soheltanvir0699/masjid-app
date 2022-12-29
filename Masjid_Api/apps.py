from django.apps import AppConfig
import os
import psutil


# from .jobs import updater
class MasjidApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Masjid_Api'

    def ready(self):
        from .jobs import updater
        updater.start()
    #     startScheduler = True
    #
    #     # check WEB_CONCURRENCY exists and is more than 1
    #     web_concurrency = os.environ.get("WEB_CONCURRENCY")
    #     if (web_concurrency):
    #         mypid = os.getpid()
    #         print("[%s] WEB_CONCURRENCY exists and is set to %s" % (mypid, web_concurrency))
    #         gunicorn_workers = int(web_concurrency)
    #         if (gunicorn_workers > 1):
    #             maxPid = self.getMaxRunningGunicornPid()
    #             if (maxPid == mypid):
    #                 startScheduler = True
    #             else:
    #                 startScheduler = False
    #
    #     if (startScheduler):
    #         print("[%s] WILL START SCHEDULER")
    #
    #     else:
    #         print("[%s] WILL NOT START SCHEDULER")
    #
    # def getMaxRunningGunicornPid(self):
    #     running_pids = psutil.pids()
    #     maxPid = -1
    #     for pid in running_pids:
    #         proc = psutil.Process(pid)
    #         proc_name = proc.name()
    #         if (proc_name == "gunicorn"):
    #             if (maxPid < pid):
    #                 maxPid = pid
    #     print("Max Gunicorn PID: %s", maxPid)
    #     return maxPid
