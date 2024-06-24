import pytz
from datetime import datetime
import logging
import traceback
import json

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from google.oauth2 import service_account

import ofscraper.classes.sessionmanager as sessionManager
import ofscraper.download.shared.utils.stats_urls as stats_urls
import ofscraper.utils.constants as constants
import ofscraper.utils.logs.helpers as log_helpers

log = logging.getLogger("shared")

# Initialize Google Sheets client and drive service globally
client = None
drive_service = None  # Initialize Drive API service
sheet = None  # Sheet object to be reused

def init_google_sheets():
    global client
    if client is None:
        scope = [
            "https://spreadsheets.google.com/feeds",
            'https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name('of-tasty-scraper-612e82dd42da.json', scope)
        client = gspread.authorize(creds)

def init_drive_service():
    global drive_service
    if drive_service is None:
        creds = service_account.Credentials.from_service_account_file(
            'of-tasty-scraper-612e82dd42da.json',
            scopes=['https://www.googleapis.com/auth/drive',
                    'https://www.googleapis.com/auth/drive.file',
                    ]
        )
        drive_service = build('drive', 'v3', credentials=creds)

def delete_existing_sheet(username):
    init_drive_service()
    try:
        query = f"name='{username}' and mimeType='application/vnd.google-apps.spreadsheet'"
        response = drive_service.files().list(q=query).execute()
        files = response.get('files', [])
        for file in files:
            drive_service.files().delete(fileId=file['id']).execute()
            log.info(f"Deleted existing sheet '{username}' with ID {file['id']}")
    except Exception as e:
        log.error(f"Error deleting existing sheet: {str(e)}")
        log.error(traceback.format_exc())
        raise e
    
def create_or_open_sheet(username):
    global sheet
    if sheet is None:
        init_google_sheets()  # Ensure client is initialized
        try:
            delete_existing_sheet(username)  # Ensure any existing sheet is deleted
            # Attempt to open the sheet if it exists
            sheet = client.open(username)
            log.info(f"Opened sheet '{sheet.title}' located at: {sheet.url}")
            return sheet, False
        except gspread.SpreadsheetNotFound:
            # Create a new sheet if it does not exist
            sheet = client.create(username)
            log.info(f"Created new sheet '{username}'")

            # Move the sheet to the desired folder using Drive API
            folder_id = '1AD0Nap0E0F0IUPfNu1Wjkckn5R68jnRA'
            try:
                move_sheet_to_folder(sheet.id, folder_id)
                log.info(f"Moved sheet '{username}' to folder '{folder_id}'")
            except Exception as e:
                log.error(f"Error moving sheet to folder: {str(e)}")
                log.error(traceback.format_exc())
                raise e

            # Add headers to the new sheet
            add_sheet_headers(sheet.sheet1)
            return sheet, True
    
    return sheet, False

def move_sheet_to_folder(sheet_id, folder_id):
    try:
        init_drive_service()  # Ensure drive_service is initialized
        
        # Retrieve the file from Google Drive API
        file = drive_service.files().get(fileId=sheet_id, fields='id, parents').execute()

        # Update the file's parents to move it to the desired folder
        previous_parents = ",".join(file.get('parents'))
        file = drive_service.files().update(
            fileId=sheet_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()
        
        log.info(f"Successfully moved sheet ID {sheet_id} to folder ID {folder_id}")

    except Exception as e:
        error_msg = f"Error moving sheet to folder: {str(e)}"
        log.error(error_msg)
        log.error(traceback.format_exc())
        raise e

def add_sheet_headers(worksheet):
    # Add headers 'Date' and the original tab names to the worksheet
    try:
        header_values = [['Date', 'Earnings - All', 'Reach - Guest', 'Reach - User', 'New Fans Subscription Earnings', 'New Fans Subscription Count']]
        worksheet.update('A1:F1', header_values)  # Update cells A1 to F1 with headers
        log.info("Added headers to the worksheet")
    except Exception as e:
        log.error(f"Error adding headers to worksheet: {str(e)}")
        log.error(traceback.format_exc())
        raise e

def write_to_sheet(username, data, column_index):
    log.info(f"Initiating write_to_sheet for column {column_index}")
    init_google_sheets()  # Ensure client is initialized  
    sheet, is_new_sheet = create_or_open_sheet(username)
    
    try:
        worksheet = sheet.sheet1  # Always use the first sheet
        log.info(f"Using worksheet {worksheet.title}")
    
        # Prepare the list of values to be written
        cell_values = [[item['date'], item['count']] for item in data]
        
        # Get the current values in the sheet
        current_values = worksheet.get_all_values()
        
        # Build a dictionary for quick lookup of existing dates, ignoring empty rows
        existing_dates = {row[0]: row for row in current_values if row}

        for row in cell_values:
            date = row[0]
            count = row[1]
            if date in existing_dates:
                if len(existing_dates[date]) < column_index + 1:
                    existing_dates[date].extend([''] * (column_index + 1 - len(existing_dates[date])))
                existing_dates[date][column_index] = count
            else:
                new_row = [date] + [''] * (column_index - 1) + [count]
                current_values.append(new_row)
        
        # Update the entire sheet with the new values
        worksheet.update('A1', current_values)
        log.info(f"Appended data to column {column_index}")
    except Exception as e:
        log.error(f"Error writing data to sheet: {str(e)}")
        log.error(traceback.format_exc())
        raise e

def fetch_and_write_data(username, column_index, fetch_url, data_key, sub_key=None, context=None):
    # init_google_sheets()  
    
    # sheet, is_new_sheet = create_or_open_sheet(username)
    # days = 180 if is_new_sheet else 1  # Use 180 days if new sheet, otherwise 1 day
    # days = 180
    days = 2
    with sessionManager.sessionManager(
        backend="httpx",
        limit=constants.getattr("API_MAX_CONNECTION"),
        retries=constants.getattr("API_INDVIDIUAL_NUM_TRIES"),
        wait_min=constants.getattr("OF_MIN_WAIT_API"),
        wait_max=constants.getattr("OF_MAX_WAIT_API"),
        new_request_auth=True,
    ) as c:
        try:
            with c.requests(fetch_url(days)) as r:
                data = r.json_()
                # adjusted_chart_amount = []
                # items = data.get(data_key, [])
                # if sub_key:
                #     items = items.get(sub_key, [])
                
                # for item in items:
                #     formatted_date = datetime.strptime(item['date'], '%Y-%m-%dT%H:%M:%S%z')
                #     adjusted_chart_amount.append({
                #         "date": formatted_date.strftime('%m-%d-%Y'),
                #         "count": item['count']
                #     })
                # log.info(f"Writing {len(adjusted_chart_amount)} items to sheet.")
                # write_to_sheet(username, adjusted_chart_amount, column_index)
                # return adjusted_chart_amount
                log.info(context)
                log.info(data)
                return data
        except Exception as E:
            log.error(f"Error fetching data: {str(E)}")
            log.error(traceback.format_exc())
            raise E

def get_earnings_all(username):
        log.info("I am here!")
        return fetch_and_write_data(username, 1, stats_urls.generate_earnings_all_url, 'total', 'chartAmount', context="Earnings - All")

def get_earnings_tips(username):
    return fetch_and_write_data(username, 2, stats_urls.generate_earnings_tips_url, 'tips', 'chartAmount', context="Tips")

def get_reach_user(username):
    return fetch_and_write_data(username, 3, stats_urls.generate_reach_user_url, 'chart', 'visitors', context="Reach User")

def get_reach_guest(username):
    return fetch_and_write_data(username, 4, stats_urls.generate_reach_guest_url, 'chart', 'visitors', context="Reach Guest")

def get_subs_fans_count_new(username):
    return fetch_and_write_data(username, 5, stats_urls.generate_subscrption_fans_count_new_url, 'subscribes', context="New Sub Count")

def get_subs_fans_earnings_new(username):
    return fetch_and_write_data(username, 6, stats_urls.generate_subscrption_fans_earnings_new_url, 'earnings', context="New Fans Sub Earnings")

def get_subs_fans_count_all(username):
    return fetch_and_write_data(username, 7, stats_urls.generate_subscrption_fans_all_count_url, 'subscribes', context="All Fan Sub Count")

def get_subs_fans_earnings_all(username):
    return fetch_and_write_data(username, 8, stats_urls.generate_subscription_fans_all_earnings_url, 'earnings', context="All Fan Earnings")

def get_subs_fans_count_renew(username):
    return fetch_and_write_data(username, 9, stats_urls.generate_subscrption_fans_count_renew_url, 'subscribes', context="Renews")

def get_earnings_chargebacks(username):
    return fetch_and_write_data(username, 10, stats_urls.generate_chargebacks_count_url, 'total', 'chartAmount', context="Chargebacks")

# def get_earnings_tips():
#     with sessionManager.sessionManager(
#         backend="httpx",
#         limit=constants.getattr("API_MAX_CONNECTION"),
#         retries=constants.getattr("API_INDVIDIUAL_NUM_TRIES"),
#         wait_min=constants.getattr("OF_MIN_WAIT_API"),
#         wait_max=constants.getattr("OF_MAX_WAIT_API"),
#         new_request_auth=True,
#     ) as c:
#         try:
#             with c.requests(stats_urls.test_generate_earnings_url(days=30)) as r:
#                 data = r.json_()
#                 # adjusted_chart_amount = []
#                 # total = data.get('total')
#                 # items = total.get('chartAmount')
                
#                 # for item in items:
#                 #     formatted_date = datetime.strptime(item['date'], '%Y-%m-%dT%H:%M:%S%z')
#                 #     adjusted_chart_amount.append({
#                 #         "date": formatted_date.strftime('%m-%d-%Y'),
#                 #         "count": item['count']
#                 #     })
#                 # log.info(f"Writing {len(adjusted_chart_amount)} items to sheet.")
#                 # write_to_sheet(username, adjusted_chart_amount, column_index)
#                 log.info(data)
#                 return data
#         except Exception as E:
#             log.error(f"Error fetching data: {str(E)}")
#             log.error(traceback.format_exc())
#             raise E
    # return fetch_and_write_data(username, 5, stats_urls.generate_earnings_tips_url, 'generate_earnings_tips_url

if __name__ == "__main__":
    init_google_sheets()
