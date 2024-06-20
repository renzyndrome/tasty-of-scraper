import logging
import traceback
import os
import asyncio
from datetime import datetime

import ofscraper.classes.media as media_class
import ofscraper.download.shared.utils.log as logs
import ofscraper.utils.settings as settings
import ofscraper.utils.text as text
from ofscraper.utils.context.run_async import run
from ofscraper.utils.paths.common import get_save_location

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup


def init_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('tasty-of-scraper-7df81f0cda17.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key('1FPEJtn4MLfm0w3kLfefZxvG9hrNo0jrM-G8v-g7O3QA').sheet1
    return sheet

from bs4 import BeautifulSoup
import re


def clean_html(raw_html):
    """
    Removes only <br> and </br> tags from the given HTML string, keeping all other elements intact.

    Args:
    raw_html (str): String containing HTML.

    Returns:
    str: String with <br> and </br> tags removed.
    """
    soup = BeautifulSoup(raw_html, "html.parser")
    
    # Remove all <br> tags
    for br in soup.find_all('br'):
        br.decompose()
    
    # Convert the soup object back to text
    clean_text = str(soup)
    
    return clean_text

@run
async def textDownloader(objectdicts, username=None):
    log = logging.getLogger("shared")
    log.info("Entering textUploader")

    sheet = init_google_sheets()

    if objectdicts is None:
        return

    try:
        objectdicts = ([objectdicts] if not isinstance(objectdicts, list) else objectdicts)
        log.info("Uploading Text Files")
        count = 0
        fails = 0
        batch_size = 50  # Define the size of each batch
        data_batch = []  # This will store each batch of data
        delay_between_batches = 60  # Delay in seconds between each batch upload

        for e in objectdicts:
            try:
                # Parse the ISO format date and reformat it
                date = datetime.strptime(e['createdAt'], "%Y-%m-%dT%H:%M:%S%z")
                formatted_date = date.strftime("%B %d, %Y %I:%M %p")

                # Clean the HTML content in the text
                clean_text = clean_html(e['text'])
                
                # text = e['text']
                data_batch.append([formatted_date, username, clean_text])
                
                # Check if the batch size is reached
                if len(data_batch) >= batch_size:
                    sheet.append_rows(data_batch)  # Upload the batch
                    count += len(data_batch)
                    data_batch = []  # Reset the batch list after uploading
                    # await asyncio.sleep(delay_between_batches)  # Wait before the next batch
            except Exception as ex:
                fails += 1
                log.error(f"Failed to prepare data for message {e['id']}: {ex}")

        # Upload any remaining data in the batch that hasn't reached the batch size
        if data_batch:
            sheet.append_rows(data_batch)
            count += len(data_batch)

        log.info(f"Uploaded {count} text files, {fails} failed")
    except Exception as E:
        log.debug(f"Issue with text {E}")
        log.debug(f"Issue with text {traceback.format_exc()}")