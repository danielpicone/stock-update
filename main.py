import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import pandas as pd
import sendgrid
import os
from sendgrid.helpers.mail import *

today_date = datetime.datetime.today().strftime('%Y-%m-%d')

# use creds to create a client to interact with the Google Drive API
def open_spreadsheet(sheet_name):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("DJP stocks").worksheet(sheet_name)
    return sheet

# def update_stock_history(sheet, history_sheet):
def update_stock_history():
    # Extract and print all of the values
    sheet = open_spreadsheet("Stock Summary")
    history_sheet = open_spreadsheet("Price history")
    today_date = datetime.datetime.today().strftime('%Y-%m-%d')
    stock_names = sheet.col_values(3)[1:]
    stock_prices = sheet.col_values(4)[1:]
    stock_units = sheet.col_values(13)[1:]
    stock_dict = dict(zip(stock_names, stock_prices))
    stock_tuple = tuple(zip(stock_names, stock_prices, stock_units))

    current_row = len(history_sheet.col_values(1))
    i = -1

    new_cells = history_sheet.range(current_row+1,1,current_row+len(stock_tuple),4)
    for cell in new_cells:
        if cell.col == 1:
            cell.value = today_date
            i += 1
        else:
            cell.value = stock_tuple[i][cell.col-2]
    history_sheet.update_cells(new_cells)

def send_email():
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("danielpicone2@gmail.com")
    to_email = Email("danielpicone2@gmail.com")
    subject = "Sending with SendGrid is Fun"
    content = Content("text/plain", "and easy to do anywhere, even with Python")
    mail = Mail(from_email, subject, to_email, content)
    # import pdb; pdb.set_trace()
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)

def get_price_history_df(end_date=today_date, start_date="2000-01-01"):
    import gspread_pandas
    worksheet = gspread_pandas.Spread("stocks", "DJP stocks")
    worksheet.open_sheet("Price history")
    history_sheet = worksheet.sheet_to_df(index=0)
    history_sheet["price"] = history_sheet["price"].apply(float)
    history_sheet["units"] = history_sheet["units"].apply(float)
    history_sheet["name"] = history_sheet["stock"].str.split(":").str[1]
    history_sheet["value"] = history_sheet.apply(lambda row: row["price"]*row["units"], axis=1)
    return history_sheet[(history_sheet["date"] >= start_date) & (history_sheet["date"] <= end_date)]

def get_min_date(sheet):
    min_date = sheet.groupby("name", as_index = False).agg({"date": "min"})
    min_date = pd.merge(min_date, sheet, left_on=["name","date"], right_on=["name","date"])\
    [["name","price","units","value"]]
    return min_date
