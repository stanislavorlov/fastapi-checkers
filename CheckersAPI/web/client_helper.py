from collections import namedtuple
from fastapi import Request
import logging
import requests

ClientContext = namedtuple('ClientContext', ['accept_language', 'region', 'agent', 'timezone'])

def get_client_context(request: Request) -> ClientContext:
    """
    Extracts client context from request headers.
    """
    accept_language = request.headers.get("accept-language", "")
    
    # Simple region detection logic based on language headers
    region = "EU" if "eu" in accept_language.lower() or "gb" in accept_language.lower() else "NA"
    
    # Timezone detection from optional header
    timezone_str = request.headers.get("x-timezone") or "UTC"
    
    # User agent
    agent = request.headers.get("user-agent", "")
    
    return ClientContext(
        accept_language=accept_language,
        region=region,
        agent=agent,
        timezone=timezone_str
    )

def get_ip_info(ip: str = "") -> dict:
    """Fetch IP and location info from ipapi.co"""
    url = f"https://ipapi.co/{ip}/json/"

    if not len(ip) or ip == "127.0.0.1":
        url = f"https://ipapi.co/json/"

    logging.debug(f"Fetching ip info: {url}")

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        logging.debug(f"ip info: {data}")

        return data
    except requests.RequestException as e:
        logging.error(f"Error fetching data: {e}")

        return {}

# asn                      : AS59577
# city                     : Lviv
# continent_code           : EU
# country                  : UA
# country_area             : 603700.0
# country_calling_code     : +380
# country_capital          : Kyiv
# country_code             : UA
# country_code_iso3        : UKR
# country_name             : Ukraine
# country_population       : 44622516
# country_tld              : .ua
# currency                 : UAH
# currency_name            : Hryvnia
# in_eu                    : False
# ip                       : 92.253.214.203
# languages                : uk,ru-UA,rom,pl,hu
# latitude                 : 49.839
# longitude                : 24.0191
# network                  : 92.253.212.0/22
# org                      : LinkCom Networks LLC
# postal                   : 79024
# region                   : Lviv
# region_code              : 46
# timezone                 : Europe/Kyiv
# utc_offset               : +0200
# version                  : IPv4