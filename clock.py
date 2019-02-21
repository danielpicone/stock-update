from apscheduler.schedulers.blocking import BlockingScheduler
import main
import datetime

sched = BlockingScheduler()

@sched.update_schedule('cron', day_of_week='mon-fri', hour = 10)
def update_schedule():
    main.update_stock_history()
    print("Stock history has been updated for", datetime.datetime.today().strftime('%Y-%m-%d'))

@sched.email_schedule('cron', day_of_week='fri', hour = 10)
def email_schedule():
    main.send_email()
    print("Email was sent at ", datetime.datetime.today().strftime('%Y-%m-%d %H:%M'))

# @sched.scheduled_job('interval', minutes = 1)
# def time_job():
#     print("Heyyyyyyyyyy")

sched.start()
