from apscheduler.schedulers.blocking import BlockingScheduler
import main
import datetime

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-fri', hour = 11)
def scheduled_job():
    main.update_stock_history()
    print("Stock history has been updated for ", datetime.datetime.today().strftime('%Y-%m-%d'))

# @sched.scheduled_job('interval', minutes = 1)
# def time_job():
#     print("Heyyyyyyyyyy")

sched.start()
