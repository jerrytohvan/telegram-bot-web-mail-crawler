
from apscheduler.schedulers.blocking import BlockingScheduler
from botcrawler import launch_evening, launch_morning, launch_noon
import requests

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=25)
def fail_safe():
    print("pinging ...")
    r = requests.get('DEPLOYED SERVER URL TO PREVENT SERVER SLEEP')

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=10, timezone= 'UTC')
def evening_posts():
 	launch_evening()

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=5, timezone= 'UTC')
def noon_posts():
 	launch_noon()

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=0, timezone= 'UTC')
def morning_posts():
 	launch_morning()

sched.start()