import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import pandas as pd
import sendgrid
import os
from sendgrid.helpers.mail import *
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import graphing
import snailmail as sm

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

# def send_email(attachment_path=None):
#     sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
#     from_email = Email("danielpicone2@gmail.com")
#     to_email = Email("danielpicone2@gmail.com")
#     subject = "Stock report for " + today_date
#     content = Content("text/plain", "This is just an update for your stock portfolio")
#     mail = Mail(from_email, subject, to_email, content)
#
#     if attachment_path:
#         import base64
#         attachment = Attachment()
#         with open(attachment_path, "rb") as f:
#             data = f.read()
#
#         encoded = base64.b64encode(data).decode()
#         attachment.content=encoded
#         attachment.type="application/pdf"
#         attachment.filename="Stock report for " + today_date + ".pdf"
#         attachment.disposition="attachment"
#         attachment.content_id="PDF Document file"
#         mail.add_attachment(attachment)
#
#
#     response = sg.client.mail.send.post(request_body=mail.get())
#     print(response.status_code)
#     print(response.body)
#     print(response.headers)

def get_price_history_df(end_date=today_date, start_date="2000-01-01"):
    import gspread_pandas
    # worksheet = gspread_pandas.Spread("stocks", "DJP stocks")
    #TODO: Create a better way to save this config
    worksheet_config = {
          "type": "service_account",
          "project_id": "djp-portfolio",
          "private_key_id": "669cd846c30e067d26d504007addfa5ad4c5bd03",
          "private_key": os.environ.get("GS_API_KEY"),
          "client_email": "portfolio@djp-portfolio.iam.gserviceaccount.com",
          "client_id": "107324578022794643121",
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://oauth2.googleapis.com/token",
          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
          "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/portfolio%40djp-portfolio.iam.gserviceaccount.com"
        }
    import pdb; pdb.set_trace()
    worksheet = gspread_pandas.Spread("stocks", "DJP stocks", config =
        {
          "type": "service_account",
          "project_id": "djp-portfolio",
          "private_key_id": "669cd846c30e067d26d504007addfa5ad4c5bd03",
          "private_key": os.environ.get("GS_API_KEY"),
          "client_email": "portfolio@djp-portfolio.iam.gserviceaccount.com",
          "client_id": "107324578022794643121",
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://oauth2.googleapis.com/token",
          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
          "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/portfolio%40djp-portfolio.iam.gserviceaccount.com"
        }
    )
    worksheet.open_sheet("Price history")
    history_sheet = worksheet.sheet_to_df(index=0)
    history_sheet["date"] = pd.to_datetime(history_sheet["date"], format = "%Y-%m-%d")
    history_sheet["price"] = history_sheet["price"].apply(float)
    history_sheet["units"] = history_sheet["units"].apply(float)
    history_sheet["name"] = history_sheet["stock"].str.split(":").str[1]
    history_sheet["value"] = history_sheet.apply(lambda row: row["price"]*row["units"], axis=1)
    return history_sheet[(history_sheet["date"] >= start_date) & (history_sheet["date"] <= end_date)]

def get_min_date(df):
    min_date = df.groupby("name", as_index = False).agg({"date": "min"})
    min_date = pd.merge(min_date, df, left_on=["name","date"], right_on=["name","date"])\
    [["name","price","units","value"]]
    return min_date

def graph_indiv_stock(file_name = "portfolio_charts.pdf"):
    # import matplotlib.pyplot as plt
    # import matplotlib.gridspec as gridspec
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.dates as mdates

    def format_date(x, pos = None):
        thisind = np.clip(int(x + 0.5), 0, N -1)
        return entire_df["date"][thisind].strftime("%Y-%m-%d")

    df = get_price_history_df(start_date = "2019-01-01")
    min_df = get_min_date(df)
    portfolio_df = df.merge(min_df[["name","value", "price"]]\
    .rename(columns={"value": "start_value", "price":"start_price"}),
        how = "left", on = "name")
    portfolio_df["stock_return"] = portfolio_df.apply(lambda row: row["price"]/row["start_price"], axis=1)
    portfolio_df = portfolio_df.merge(portfolio_df.groupby("date", as_index=False)\
        .agg({"value":"sum"}).rename(columns={"value":"portfolio_value"}),
        how = "left", on = "date")
    portfolio_df["proportion"] = portfolio_df.apply(lambda row: row["value"]/row["portfolio_value"], axis=1)
    portfolio_df["return_proportion"] = portfolio_df.apply(lambda row: row["stock_return"]*row["proportion"], axis=1)
    names = portfolio_df["name"].unique()

    with PdfPages(file_name) as pdf:
        entire_df = portfolio_df.groupby("date", as_index = False).agg({"return_proportion":"sum"})
        plt.figure(tight_layout = True)
        N = len(entire_df.date)
        plt.plot(range(len(entire_df.date)), entire_df["return_proportion"].tolist(), "-")
        plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
        plot_formatter(plt)
        plt.title("Return of total portfolio")
        pdf.savefig()
        plt.close()
        for (i, s) in enumerate(names):
            plt.figure(tight_layout = True)
            gs = gridspec.GridSpec(len(names), 1)
            stock_df = portfolio_df[portfolio_df["name"]==s]
            N = len(stock_df.date)
            x_axis = range(len(stock_df["date"]))
            plt.plot(x_axis, stock_df["stock_return"].tolist(), "-")
            plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
            plt.gca().set_ylim(0.95*portfolio_df["stock_return"].min(),
                1.05*portfolio_df["stock_return"].max())
            plot_formatter(plt)
            plt.title("Return of " + s)
            pdf.savefig()
            plt.close()


def plot_formatter(plot):
    years = mdates.YearLocator()
    months = mdates.MonthLocator()
    days = mdates.DayLocator()
    plt.grid(True)

# def generate_email(file_name = "portfolio_charts.pdf"):
#     graph_indiv_stock(file_name)
#     send_email(file_name)
#     return True

# snailmail.generate_email()
