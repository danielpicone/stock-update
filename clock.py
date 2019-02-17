from apscheduler.schedulers.blocking import BlockingScheduler
import main

sched = BlockingScheduler()

#@sched.scheduled_job('cron', day_of_week='mon-fri', hour = 11)
#def scheduled_job():
    #main.update_history()

@sched.scheduled_job('interval', minutes = 1)
def time_job():
    print("Heyyyyyyyyyy")

sched.start()
