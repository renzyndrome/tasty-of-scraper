from datetime import datetime, timedelta
from urllib.parse import urlencode, quote

def generate_earnings_url():
    base_url = "https://onlyfans.com/api2/v2/earnings/chart?"
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Format dates for URL
    date_format = "%Y-%m-%d %H:%M:%S"
    params = {
        'startDate': start_date.strftime(date_format),
        'endDate': end_date.strftime(date_format),
        'withTotal': 'true',
        'filter[total_count]': 'total_count',
        'filter[total_amount]': 'total_amount',
        'filter[subscribes_count]': 'subscribes_count',
        'filter[subscribes_amount]': 'subscribes_amount',
        'filter[tips_count]': 'tips_count',
        'filter[tips_amount]': 'tips_amount',
        'filter[messages_count]': 'messages_count',
        'filter[messages_amount]': 'messages_amount',
        'filter[post_count]': 'post_count',
        'filter[post_amount]': 'post_amount',
        'filter[stream_count]': 'stream_count',
        'filter[stream_amount]': 'stream_amount',
        'filter[tips_profile_count]': 'tips_profile_count',
        'filter[tips_profile_amount]': 'tips_profile_amount',
        'filter[tips_chat_count]': 'tips_chat_count',
        'filter[tips_chat_amount]': 'tips_chat_amount',
        'filter[tips_post_count]': 'tips_post_count',
        'filter[tips_post_amount]': 'tips_post_amount',
        'filter[tips_stream_count]': 'tips_stream_count',
        'filter[tips_stream_amount]': 'tips_stream_amount',
        'filter[tips_story_count]': 'tips_story_count',
        'filter[tips_story_amount]': 'tips_story_amount',
        # Add new filters here
        'filter[new_subscribers_count]': 'new_subscribers_count',
        'filter[chargebacks_count]': 'chargebacks_count',
        'filter[refunds_amount]': 'refunds_amount',
    }
    
    # Encode parameters and create full URL
    url_encoded_params = urlencode(params, quote_via=lambda s, safe, encoding=None, errors=None: quote(s, safe=''))
    full_url = base_url + url_encoded_params
    
    return full_url


def generate_reach_guest_url(start_date=None, end_date=None):
    base_url = "https://onlyfans.com/api2/v2/users/me/profile/stats?"
    
    # Calculate date range
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=30)
    
    # Format dates for URL
    date_format = "%Y-%m-%d %H:%M:%S"
    params = {
        'startDate': start_date.strftime(date_format),
        'endDate': end_date.strftime(date_format),
        'by': 'guests',
        'filter[]': 'chart',
    }
    
    # Encode parameters and create full URL
    url_encoded_params = urlencode(params, quote_via=lambda s, safe, encoding=None, errors=None: quote(s, safe=''))
    full_url = base_url + url_encoded_params
    
    return full_url


def generate_reach_user_url(start_date=None, end_date=None):
    base_url = "https://onlyfans.com/api2/v2/users/me/profile/stats?"
    
    # Calculate date range
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=30)
    
    # Format dates for URL
    date_format = "%Y-%m-%dT%H:%M:%S"
    params = {
        'startDate': start_date.strftime(date_format),
        'endDate': end_date.strftime(date_format),
        'by': 'users',
        'filter[]': 'chart',
    }
    
    # Encode parameters and create full URL
    url_encoded_params = urlencode(params, quote_via=lambda s, safe, encoding=None, errors=None: quote(s, safe=''))
    full_url = base_url + url_encoded_params
    
    return full_url

def generate_subscription_fans_all_url(start_date=None, end_date=None):
    base_url = "https://onlyfans.com/api2/v2/subscriptions/subscribers/chart?"
    
    # Calculate date range
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=30)
    
    # Format dates for URL
    date_format = "%Y-%m-%d %H:%M:%S"
    params = {
        'startDate': start_date.strftime(date_format),
        'endDate': end_date.strftime(date_format),
        'by': 'total',
    }
    
    # Encode parameters and create full URL
    url_encoded_params = urlencode(params, quote_via=lambda s, safe, encoding=None, errors=None: quote(s, safe=''))
    full_url = base_url + url_encoded_params
    
    return full_url


def generate_subscrption_fans_new_url(start_date=None, end_date=None):
    base_url = "https://onlyfans.com/api2/v2/subscriptions/subscribers/chart?"
    
    # Calculate date range
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=30)
    
    # Format dates for URL
    date_format = "%Y-%m-%d %H:%M:%S"
    params = {
        'startDate': start_date.strftime(date_format),
        'endDate': end_date.strftime(date_format),
        'by': 'new',
    }
    
    # Encode parameters and create full URL
    url_encoded_params = urlencode(params, quote_via=lambda s, safe, encoding=None, errors=None: quote(s, safe=''))
    full_url = base_url + url_encoded_params
    
    return full_url
