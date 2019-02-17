import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import pandas as pd


# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("DJP stocks").worksheet("Stock Summary")

# Extract and print all of the values
# list_of_hashes = sheet.get_all_records()
# print(list_of_hashes)

today_date = datetime.datetime.today().strftime('%Y-%m-%d')
stock_names = sheet.col_values(3)[1:]
stock_prices = sheet.col_values(4)[1:]
stock_dict = dict(zip(stock_names, stock_prices))
stock_tuple = tuple(zip(stock_names, stock_prices))

history_sheet = client.open("DJP stocks").worksheet("Price history")

current_row = len(history_sheet.col_values(1))
i = -1

new_cells = history_sheet.range(current_row+1,1,current_row+len(stock_dict),3)
for cell in new_cells:
    if cell.col == 1:
        cell.value = today_date
        i += 1
    else:
        cell.value = stock_tuple[i][cell.col-2]
history_sheet.update_cells(new_cells)
