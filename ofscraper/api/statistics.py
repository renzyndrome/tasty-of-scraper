import pytz
from datetime import datetime
import logging
import traceback
import json
import inspect

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2 import service_account

import ofscraper.classes.sessionmanager as sessionManager
import ofscraper.download.shared.utils.stats_urls as stats_urls
import ofscraper.utils.constants as constants
import ofscraper.utils.logs.helpers as log_helpers

log = logging.getLogger("shared")

# Initialize Google Sheets client globally
client = None
drive_service = None  # Initialize Drive API service

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

def create_or_open_sheet(username):
    init_google_sheets()  # Ensure client is initialized
    init_drive_service()
    try:
        # Attempt to open the sheet if it exists
        sheet = client.open(username)
        log.info(f"Opened sheet '{sheet}' located at: {sheet.url}")

        

    except gspread.SpreadsheetNotFound:
        # Create a new sheet if it does not exist
        sheet = client.create(username)
        log.info(f"Created new sheet '{username}'")

        # Delete the default Sheet1
        default_sheet = sheet.worksheet("Sheet1")
        sheet.del_worksheet(default_sheet)

        # Move the sheet to the desired folder using Drive API
    folder_id = '1AD0Nap0E0F0IUPfNu1Wjkckn5R68jnRA'
    try:
        move_sheet_to_folder(sheet.id, folder_id)
        log.info(f"Moved sheet '{username}' to folder '{folder_id}'")
    except Exception as e:
        log.error(f"Error moving sheet to folder: {str(e)}")
        log.error(traceback.format_exc())
        raise e
        
        # Add headers only when creating a new sheet
        add_sheet_headers(sheet)
    except Exception as e:
        log.error(f"Error creating or opening sheet: {str(e)}")
        log.error(traceback.format_exc())
        raise e
    
    return sheet


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

    except Exception as e:
        error_msg = f"Error moving sheet to folder: {str(e)}"
        log.error(error_msg)
        log.error(traceback.format_exc())
        raise e



def add_sheet_headers(worksheet):
    # Add headers 'Date' and 'Count' to the worksheet
    try:
        header_values = [['Date', 'Count']]  # Provide headers as a list of lists
        worksheet.update('A1:B1', header_values)  # Update cells A1 and B1 with headers
    except Exception as e:
        log.error(f"Error adding headers to worksheet: {str(e)}")
        log.error(traceback.format_exc())
        raise e


def write_to_sheet(username, data, tab_name):
    log.info("Initiating write_to_sheet")
    init_google_sheets()  # Ensure client is initialized  
    sheet = create_or_open_sheet(username)
    
    try:
        # Try to select the worksheet if it exists
        worksheet = sheet.worksheet(tab_name)
        log.info(f"Worksheet {username} found")
    except gspread.WorksheetNotFound:
        # Create a new worksheet if it does not exist
        worksheet = sheet.add_worksheet(title=tab_name, rows="365", cols="2")
        add_sheet_headers(worksheet)  # Add headers for the new worksheet
        log.info(f"Created {username} worksheet")
    
    try:
        # Prepare the list of values to be written
        cell_values = [[item['date'], item['count']] for item in data]
        # Write data starting from the second row
        worksheet.append_rows(cell_values)
        log.info(f"Appended data to {tab_name}")
    except Exception as e:
        log.error(f"Error writing data to sheet: {str(e)}")
        log.error(traceback.format_exc())
        raise e


def get_earnings_all(username):
    # Fetch earnings data and write to Google Sheets
    with sessionManager.sessionManager(
        backend="httpx",
        limit=constants.getattr("API_MAX_CONNECTION"),
        retries=constants.getattr("API_INDVIDIUAL_NUM_TRIES"),
        wait_min=constants.getattr("OF_MIN_WAIT_API"),
        wait_max=constants.getattr("OF_MAX_WAIT_API"),
        new_request_auth=True,
    ) as c:
        try:
            init_google_sheets()  
            
            # with c.requests(constants.getattr("earningsEP60D")) as r:
            with c.requests(stats_urls.generate_earnings_url()) as r:
                data = r.json_()
                adjusted_chart_amount = []
                if 'total' in data and 'chartAmount' in data['total']:
                    log.info("Getting chartAmount")
                    for item in data['total']['chartAmount']:
                        formatted_date = datetime.strptime(item['date'], '%Y-%m-%dT%H:%M:%S%z')
                        # pst_time = utc_time.astimezone(pytz.timezone('America/Los_Angeles'))
                        adjusted_chart_amount.append({
                            # "date": pst_time.strftime('%Y-%m-%d'),
                            "date": formatted_date.strftime('%m-%d-%Y'),
                            "count": item['count']
                        })
                    log.info(f"Earnings appended to sheets")
                log.info(f"Writing {len(adjusted_chart_amount)} items to sheet.")
                write_to_sheet(username, adjusted_chart_amount, tab_name="Earnings - All")
                
                return adjusted_chart_amount
        except Exception as E:
            log.error(f"Error fetching earnings data: {str(E)}")
            log.error(traceback.format_exc())
            raise E

def get_reach_guest(username):

    with sessionManager.sessionManager(
        backend="httpx",
        limit=constants.getattr("API_MAX_CONNECTION"),
        retries=constants.getattr("API_INDVIDIUAL_NUM_TRIES"),
        wait_min=constants.getattr("OF_MIN_WAIT_API"),
        wait_max=constants.getattr("OF_MAX_WAIT_API"),
        new_request_auth=True,
    ) as c:
        try:
            init_google_sheets()  # Ensure client is initialized
            
            with c.requests(stats_urls.generate_reach_guest_url()) as r:
                data = r.json_()
                adjusted_chart_amount = []
                if 'chart' in data and 'visitors' in data['chart']:
                    log.info("Getting Visitors")
                    for item in data['chart']['visitors']:
                        formatted_date = datetime.strptime(item['date'], '%Y-%m-%dT%H:%M:%S%z')
                        adjusted_chart_amount.append({
                            # "date": pst_time.strftime('%Y-%m-%d'),
                            "date": formatted_date.strftime('%m-%d-%Y'),
                            "count": item['count']
                        })
                    log.info(f"Reach - Guest appended to sheets")
                write_to_sheet(username, adjusted_chart_amount, tab_name="Reach - Guest")
                
                return adjusted_chart_amount
        except Exception as E:
            log.error(f"Error fetching reach - guest data: {str(E)}")
            log.error(traceback.format_exc())
            raise E

def get_reach_user(username):
    with sessionManager.sessionManager(
        backend="httpx",
        limit=constants.getattr("API_MAX_CONNECTION"),
        retries=constants.getattr("API_INDVIDIUAL_NUM_TRIES"),
        wait_min=constants.getattr("OF_MIN_WAIT_API"),
        wait_max=constants.getattr("OF_MAX_WAIT_API"),
        new_request_auth=True,
    ) as c:
        try:
            init_google_sheets() 
            
            with c.requests(stats_urls.generate_reach_user_url()) as r:
                data = r.json_()
                adjusted_chart_amount = []
                if 'chart' in data and 'visitors' in data['chart']:
                    log.info("Getting Visitors")
                    for item in data['chart']['visitors']:
                        formatted_date = datetime.strptime(item['date'], '%Y-%m-%dT%H:%M:%S%z')
                        adjusted_chart_amount.append({
                            "date": formatted_date.strftime('%m-%d-%Y'),
                            "count": item['count']
                        })
                    log.info(f"Reach - Guest appended to sheets")
                write_to_sheet(username, adjusted_chart_amount, tab_name="Reach - User")
                
                return adjusted_chart_amount
        except Exception as E:
            log.error(f"Error fetching reach - user data: {str(E)}")
            log.error(traceback.format_exc())
            raise E
        
def get_subs_fans_all(username):
    with sessionManager.sessionManager(
        backend="httpx",
        limit=constants.getattr("API_MAX_CONNECTION"),
        retries=constants.getattr("API_INDVIDIUAL_NUM_TRIES"),
        wait_min=constants.getattr("OF_MIN_WAIT_API"),
        wait_max=constants.getattr("OF_MAX_WAIT_API"),
        new_request_auth=True,
    ) as c:
        try:
            init_google_sheets()  
            
            with c.requests(stats_urls.generate_subscription_fans_all_url()) as r:
                data = r.json_()
                adjusted_chart_amount = []
                if 'earnings' in data :
                    log.info("Getting Visitors")
                    for item in data['earnings']:
                        formatted_date = datetime.strptime(item['date'], '%Y-%m-%dT%H:%M:%S%z')
                        adjusted_chart_amount.append({
                            "date": formatted_date.strftime('%m-%d-%Y'),
                            "count": item['count']
                        })
                    log.info(f"Fans Subscription - All appended to sheets")
                write_to_sheet(username, adjusted_chart_amount, tab_name="Fans Subscription - All")
                
                return adjusted_chart_amount
        except Exception as E:
            log.error(f"Error fetching fans subs - all data: {str(E)}")
            log.error(traceback.format_exc())
            raise E

def get_subs_fans_new(username):
    with sessionManager.sessionManager(
        backend="httpx",
        limit=constants.getattr("API_MAX_CONNECTION"),
        retries=constants.getattr("API_INDVIDIUAL_NUM_TRIES"),
        wait_min=constants.getattr("OF_MIN_WAIT_API"),
        wait_max=constants.getattr("OF_MAX_WAIT_API"),
        new_request_auth=True,
    ) as c:
        try:
            init_google_sheets()  
            
            with c.requests(stats_urls.generate_subscrption_fans_new_url()) as r:
                data = r.json_()
                adjusted_chart_amount = []
                if 'earnings' in data :
                    log.info("Getting Visitors")
                    for item in data['earnings']:
                        formatted_date = datetime.strptime(item['date'], '%Y-%m-%dT%H:%M:%S%z')
                        adjusted_chart_amount.append({
                            # "date": pst_time.strftime('%Y-%m-%d'),
                            "date": formatted_date.strftime('%m-%d-%Y'),
                            "count": item['count']
                        })
                    log.info(f"Fans Subscription - New appended to sheets")
                write_to_sheet(username, adjusted_chart_amount, tab_name="Fans Subscription - New")
                
                return adjusted_chart_amount
        except Exception as E:
            log.error(f"Error fetching fans subs - new data: {str(E)}")
            log.error(traceback.format_exc())
            raise E


if __name__ == "__main__":
    init_google_sheets()  
