r"""
                                                             
 _______  _______         _______  _______  _______  _______  _______  _______  _______ 
(  ___  )(  ____ \       (  ____ \(  ____ \(  ____ )(  ___  )(  ____ )(  ____ \(  ____ )
| (   ) || (    \/       | (    \/| (    \/| (    )|| (   ) || (    )|| (    \/| (    )|
| |   | || (__     _____ | (_____ | |      | (____)|| (___) || (____)|| (__    | (____)|
| |   | ||  __)   (_____)(_____  )| |      |     __)|  ___  ||  _____)|  __)   |     __)
| |   | || (                   ) || |      | (\ (   | (   ) || (      | (      | (\ (   
| (___) || )             /\____) || (____/\| ) \ \__| )   ( || )      | (____/\| ) \ \__
(_______)|/              \_______)(_______/|/   \__/|/     \||/       (_______/|/   \__/
                                                                                      
"""

import logging
import traceback
import json

import ofscraper.classes.sessionmanager as sessionManager
import ofscraper.utils.constants as constants
import ofscraper.utils.logs.helpers as log_helpers

log = logging.getLogger("shared")


def scrape_user():
    with sessionManager.sessionManager(
        backend="httpx",
        limit=constants.getattr("API_MAX_CONNECTION"),
        retries=constants.getattr("API_INDVIDIUAL_NUM_TRIES"),
        wait_min=constants.getattr("OF_AUTH_MIN_WAIT"),
        wait_max=constants.getattr("OF_AUTH_MAX_WAIT"),
        new_request_auth=True,
    ) as c:
        return _scraper_user_helper(c)


def _scraper_user_helper(c):
    try:
        with c.requests(constants.getattr("meEP")) as r:
            data = r.json_()
            log_helpers.updateSenstiveDict(data["id"], "userid")
            log_helpers.updateSenstiveDict(
                f"{data['username']} | {data['username']}|\\b{data['username']}\\b",
                "username",
            )
            log_helpers.updateSenstiveDict(
                f"{data['name']} | {data['name']}|\\b{data['name']}\\b",
                "name",
            )

    except Exception as E:
        log.traceback_(E)
        log.traceback_(traceback.format_exc())
        raise E
    return data


def parse_subscriber_count():
    with sessionManager.sessionManager(
        backend="httpx",
        limit=constants.getattr("API_MAX_CONNECTION"),
        retries=constants.getattr("API_INDVIDIUAL_NUM_TRIES"),
        wait_min=constants.getattr("OF_MIN_WAIT_API"),
        wait_max=constants.getattr("OF_MAX_WAIT_API"),
        new_request_auth=True,
    ) as c:
        try:
            with c.requests(constants.getattr("subscribeCountEP")) as r:
                data = r.json_()
                return (
                    data["subscriptions"]["active"],
                    data["subscriptions"]["expired"],
                )

        except Exception as E:
            log.traceback_(E)
            log.traceback_(traceback.format_exc())
            raise E
import pytz
from datetime import datetime
def get_earnings():
    with sessionManager.sessionManager(
        backend="httpx",
        limit=constants.getattr("API_MAX_CONNECTION"),
        retries=constants.getattr("API_INDVIDIUAL_NUM_TRIES"),
        wait_min=constants.getattr("OF_MIN_WAIT_API"),
        wait_max=constants.getattr("OF_MAX_WAIT_API"),
        new_request_auth=True,
    ) as c:
        try:
            with c.requests(constants.getattr("earningsEP60D")) as r:
                log = logging.getLogger("shared")
                
                data = r.json_()
                # Initialize an empty list to store the adjusted date and count
                adjusted_chart_amount = []
                # log.info(data)
                # Convert each date in chartAmount to PST and store only date and count
    
                if 'total' in data and 'chartAmount' in data['total']:
                    log.info(f"Getting chartAmount")
                    for item in data['total']['chartAmount']:
                        utc_time = datetime.strptime(item['date'], '%Y-%m-%dT%H:%M:%S%z')
                        pst_time = utc_time.astimezone(pytz.timezone('America/Los_Angeles'))
                        adjusted_chart_amount.append({
                            "date": pst_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                            "count": item['count']
                        })
                        log.info(f"Converted {item['date']} earnings ${item['count']} to {pst_time.strftime('%Y-%m-%d %H:%M:%S %Z')} earnings ${item['count']}")

         
                return adjusted_chart_amount
        except Exception as E:
            log.traceback_(E)
            log.traceback_(traceback.format_exc())
            raise E
        # chartAmount
    # earnings_info = get_earnings()
    # return earnings_info
    # print(json.dumps(earnings_info, indent=4))
def get_check():
    with sessionManager.sessionManager(
        backend="httpx",
        limit=constants.getattr("API_MAX_CONNECTION"),
        retries=constants.getattr("API_INDVIDIUAL_NUM_TRIES"),
        wait_min=constants.getattr("OF_MIN_WAIT_API"),
        wait_max=constants.getattr("OF_MAX_WAIT_API"),
        new_request_auth=True,
    ) as c:
        try:
            with c.requests(constants.getattr("checkEp")) as r:
                data = r.json_()
                # Assuming the data structure includes 'total_earnings' and 'reach'
                return data
                # total_earnings = data.get('total_earnings', 0)
                # reach = data.get('reach', 0)
                # return {
                #     "total_earnings": total_earnings,
                #     "reach": reach
                # }
        except Exception as E:
            log.traceback_(E)
            log.traceback_(traceback.format_exc())
            raise E

def get_reach_guest():
    with sessionManager.sessionManager(
        backend="httpx",
        limit=constants.getattr("API_MAX_CONNECTION"),
        retries=constants.getattr("API_INDVIDIUAL_NUM_TRIES"),
        wait_min=constants.getattr("OF_MIN_WAIT_API"),
        wait_max=constants.getattr("OF_MAX_WAIT_API"),
        new_request_auth=True,
    ) as c:
        try:
            with c.requests(constants.getattr("guestEP60D")) as r:
                data = r.json_()
                return data

        except Exception as E:
            log.traceback_(E)
            log.traceback_(traceback.format_exc())
            raise E

def get_reach_user():
    with sessionManager.sessionManager(
        backend="httpx",
        limit=constants.getattr("API_MAX_CONNECTION"),
        retries=constants.getattr("API_INDVIDIUAL_NUM_TRIES"),
        wait_min=constants.getattr("OF_MIN_WAIT_API"),
        wait_max=constants.getattr("OF_MAX_WAIT_API"),
        new_request_auth=True,
    ) as c:
        try:
            with c.requests(constants.getattr("userEP60D")) as r:
                data = r.json_()
                return data

        except Exception as E:
            log.traceback_(E)
            log.traceback_(traceback.format_exc())
            raise E
        
def get_fans_all():
    with sessionManager.sessionManager(
        backend="httpx",
        limit=constants.getattr("API_MAX_CONNECTION"),
        retries=constants.getattr("API_INDVIDIUAL_NUM_TRIES"),
        wait_min=constants.getattr("OF_MIN_WAIT_API"),
        wait_max=constants.getattr("OF_MAX_WAIT_API"),
        new_request_auth=True,
    ) as c:
        try:
            with c.requests(constants.getattr("fansAllEP7D")) as r:
                data = r.json_()
                return data

        except Exception as E:
            log.traceback_(E)
            log.traceback_(traceback.format_exc())
            raise E
        
def get_fans_all_60():
    with sessionManager.sessionManager(
        backend="httpx",
        limit=constants.getattr("API_MAX_CONNECTION"),
        retries=constants.getattr("API_INDVIDIUAL_NUM_TRIES"),
        wait_min=constants.getattr("OF_MIN_WAIT_API"),
        wait_max=constants.getattr("OF_MAX_WAIT_API"),
        new_request_auth=True,
    ) as c:
        try:
            with c.requests(constants.getattr("fansAllEP60D")) as r:
                data = r.json_()
                return data

        except Exception as E:
            log.traceback_(E)
            log.traceback_(traceback.format_exc())
            raise E
        
def get_fans_new_60():
    with sessionManager.sessionManager(
        backend="httpx",
        limit=constants.getattr("API_MAX_CONNECTION"),
        retries=constants.getattr("API_INDVIDIUAL_NUM_TRIES"),
        wait_min=constants.getattr("OF_MIN_WAIT_API"),
        wait_max=constants.getattr("OF_MAX_WAIT_API"),
        new_request_auth=True,
    ) as c:
        try:
            with c.requests(constants.getattr("fansNewEP60D")) as r:
                data = r.json_()
                return data

        except Exception as E:
            log.traceback_(E)
            log.traceback_(traceback.format_exc())
            raise E