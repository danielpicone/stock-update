from apscheduler.schedulers.blocking import BlockingScheduler
import main
import datetime

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-fri', hour = 9)
def update_schedule():
    main.update_stock_history()
    print("Stock history has been updated for", datetime.datetime.today().strftime('%Y-%m-%d'))

@sched.scheduled_job('cron', day_of_week='fri', hour = 9)
# @sched.scheduled_job('interval', minutes = 1)
def email_schedule():
    main.generate_email("Stock report.pdf")
    print("Email was sent at ", datetime.datetime.today().strftime('%Y-%m-%d %H:%M'))

# @sched.scheduled_job('interval', minutes = 1)
# def time_job():
#     print("Heyyyyyyyyyy")

sched.start()
