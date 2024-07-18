from datetime import datetime, timedelta
from urllib.parse import urlencode, quote


def generate_chargebacks_url():
    base_url = "https://onlyfans.com/api2/v2/earnings/chart?"
    vault_url = "https://onlyfans.com/api2/v2/vault/lists?view=main&offset=0&limit=10"

    # Calculate date range
    end_date = datetime.now()
    # start_date = end_date - timedelta(days=days)

    # Format dates for URL
    date_format = "%Y-%m-%d %H:%M:%S"
    # params = {
    #     'view': offset,
    #     'endDate': end_date.strftime(date_format),
    #     'withTotal': 'true',
    #     'filter[chargebacks_count]': 'chargebacks_count',
    # }

    # Encode parameters and create full URL
    url_encoded_params = urlencode(
        quote_via=lambda s, safe, encoding=None, errors=None: quote(s, safe=''))
    full_url = base_url + url_encoded_params

    return full_url
