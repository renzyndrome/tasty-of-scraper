import pytz
from datetime import datetime
import logging
import traceback
import json
import time
import os

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

header_contexts = []
CONTEXTS_FILE = 'header_contexts.json'


def load_header_contexts(username):
    global header_contexts
    contexts_file = f'header_contexts_{username}.json'
    if os.path.exists(contexts_file):
        try:
            with open(contexts_file, 'r') as file:
                header_contexts = json.load(file).get('contexts', [])
                log.info(f"Loaded header contexts for username '{
                         username}': {header_contexts}")
        except json.JSONDecodeError as e:
            log.error(f"Error decoding JSON from file '{
                      contexts_file}': {str(e)}")
            header_contexts = []  # Handle this case appropriately
    else:
        header_contexts = []


def save_header_contexts(username, sheet_id):
    contexts_file = f'header_contexts_{username}.json'
    with open(contexts_file, 'w') as file:
        json.dump({'contexts': header_contexts, 'sheet_id': sheet_id}, file)
        log.info(f"Saved header contexts with sheet ID '{
                 sheet_id}' for username '{username}'")


def init_google_sheets():
    global client
    if client is None:
        scope = [
            "https://spreadsheets.google.com/feeds",
            'https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            'of-tasty-scraper-612e82dd42da.json', scope)
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
        query = f"name='{
            username}' and mimeType='application/vnd.google-apps.spreadsheet'"
        response = drive_service.files().list(q=query).execute()
        files = response.get('files', [])
        for file in files:
            drive_service.files().delete(fileId=file['id']).execute()
            log.info(f"Deleted existing sheet '{
                     username}' with ID {file['id']}")
    except Exception as e:
        log.error(f"Error deleting existing sheet: {str(e)}")
        log.error(traceback.format_exc())
        raise e


def create_or_open_sheet(username):
    init_google_sheets()  # Ensure client is initialized
    try:
        # Load header contexts from file
        load_header_contexts(username)

        # Check if there's an existing sheet ID in the loaded contexts
        contexts_file = f'header_contexts_{username}.json'
        if os.path.exists(contexts_file):
            with open(contexts_file, 'r') as file:
                existing_contexts = json.load(file)
                if 'sheet_id' in existing_contexts:
                    sheet_id = existing_contexts['sheet_id']
                    try:
                        sheet = client.open_by_key(sheet_id)
                        log.info(f"Opened existing sheet '{sheet.title}' with ID '{
                                 sheet_id}' for username '{username}'")
                        return sheet, False
                    except gspread.SpreadsheetNotFound:
                        log.info(f"Sheet with ID '{
                                 sheet_id}' not found. Creating a new sheet.")

        # Create a new sheet if it does not exist
        sheet = client.create(username)
        log.info(f"Created new sheet '{username}'")

        # Move the sheet to the desired folder using Drive API
        folder_id = '1w3fznwgphEy-AFh8lMorShNty9U-ZDxt'
        try:
            move_sheet_to_folder(sheet.id, folder_id)
            log.info(f"Moved sheet '{username}' to folder '{folder_id}'")
        except Exception as e:
            log.error(f"Error moving sheet to folder: {str(e)}")
            log.error(traceback.format_exc())
            raise e

        # Add headers to the new sheet
        add_sheet_headers(sheet.sheet1)
        log.info("New sheet created. Using 180 days coverage.")

        # Save the sheet ID to the contexts file
        save_header_contexts(username, sheet.id)

        return sheet, True

    except Exception as e:
        log.error(f"Error creating or opening sheet: {str(e)}")
        log.error(traceback.format_exc())
        raise e


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

        log.info(f"Successfully moved sheet ID {
                 sheet_id} to folder ID {folder_id}")

    except Exception as e:
        error_msg = f"Error moving sheet to folder: {str(e)}"
        log.error(error_msg)
        log.error(traceback.format_exc())
        raise e


def add_sheet_headers(worksheet):
    # Add headers 'Date' and all contexts to the worksheet
    try:
        global header_contexts
        header_values = [['Date'] + header_contexts]
        # Update cells starting at A1 with headers
        worksheet.update('A1', header_values)
        log.info("Added headers to the worksheet")
    except Exception as e:
        log.error(f"Error adding headers to worksheet: {str(e)}")
        log.error(traceback.format_exc())
        raise e


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


def fetch_and_write_data(username, column_index, fetch_url, data_key, sub_key=None, context=None):
    global header_contexts
    load_header_contexts(username)
    sheet, is_new_sheet = create_or_open_sheet(username)

    # Detect if this is a new context added during this run
    is_new_context = context and context not in header_contexts
    if is_new_context:
        header_contexts.append(context)
        # Save updated contexts including sheet ID
        save_header_contexts(username, sheet.id)

    # Use 180 days if new context or new sheet, otherwise 3 day
    days = 180 if is_new_context or is_new_sheet else 3
    # days = 2
    log.info(f"Sheet status: {'New' if is_new_sheet else 'Existing'}, Context status: {
             'New' if is_new_context else 'Existing'}")

    retries = 3
    retry_delay = 5  # seconds

    for attempt in range(retries):
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
                    adjusted_chart_amount = []
                    items = data.get(data_key, [])
                    if sub_key:
                        if isinstance(items, list):
                            items = [item[sub_key]
                                     for item in items if sub_key in item]
                        else:
                            items = items.get(sub_key, [])

                    for item in items:
                        formatted_date = datetime.strptime(
                            item['date'], '%Y-%m-%dT%H:%M:%S%z')
                        if context == "Earning - All":
                            count_with_currency = f"${item['count']}"
                        else:
                            count_with_currency = item['count']
                        adjusted_chart_amount.append({
                            "date": formatted_date.strftime('%m-%d-%Y'),
                            "count": count_with_currency
                        })

                    # Sort by date in ascending order (oldest first)
                    # adjusted_chart_amount.sort(
                    #     key=lambda x: datetime.strptime(x['date'], '%m-%d-%Y'))
                    adjusted_chart_amount.sort(
                        key=lambda x: x['date'], reverse=True)
                    log.info(
                        f"Writing {len(adjusted_chart_amount)} items to {context}.")
                    update_headers_if_needed(sheet)
                    write_to_sheet(
                        username, adjusted_chart_amount, column_index, sheet)
                    return adjusted_chart_amount
            except Exception as E:
                log.error(f"Error fetching data: {str(E)}")
                log.error(traceback.format_exc())
                if attempt < retries - 1:
                    log.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise E


def update_headers_if_needed(sheet):
    worksheet = sheet.sheet1  # Always use the first sheet
    current_headers = worksheet.row_values(1)
    expected_headers = ['Date'] + header_contexts

    if current_headers != expected_headers:
        header_values = [expected_headers]
        # Update cells starting at A1 with headers
        worksheet.update('A1', header_values)
        log.info("Updated headers in the worksheet")


def write_to_sheet(username, data, column_index, sheet):
    init_google_sheets()  # Ensure client is initialized
    sheet, is_new_sheet = create_or_open_sheet(username)

    try:
        worksheet = sheet.sheet1  # Always use the first sheet

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
                    existing_dates[date].extend(
                        [''] * (column_index + 1 - len(existing_dates[date])))
                existing_dates[date][column_index] = count
            else:
                new_row = [date] + [''] * (column_index - 1) + [count]
                current_values.append(new_row)

        # Update the entire sheet with the new values
        worksheet.update('A1', current_values)
        log.info(f"Appended data successfully!")
    except Exception as e:
        log.error(f"Error writing data to sheet: {str(e)}")
        log.error(traceback.format_exc())
        raise e


def get_earnings_all(username):
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
    return fetch_and_write_data(username, 10, stats_urls.generate_chargebacks_count_url, 'chartAmount', context="Chargebacks")


if __name__ == "__main__":
    init_google_sheets()
