import requests
import sys
from bs4 import BeautifulSoup
import time

"""Query module

This module contains a function to make calls to an API.

"""

JSON = 0
HTML = 1


def query_site(url, params, fmt=JSON):
    """Makes a query to an API.

    :param url:     -- string with base url for the query
    :param params:  -- dictionary with the params for the query (default empty dictionary)
    :param fmt:     -- the format in which the response has to be returned (default JSON)
    :return:        -- a format object with the response to the query

    :raises:        -- HTTPError if the HTTP request returned an unsuccessful status code.

    """

    try:
        r = requests.get(url, params=params)

        while r.status_code != requests.codes.ok:
            print("Request limit reached!\n")
            time.sleep(60)
            r = requests.get(url, params=params)

        return {
            JSON: __get_json,
            HTML: __get_html
        }[fmt](r)

    except ConnectionAbortedError:
        print("There was an unexpected exception because the internet connection was cut. After 100 seconds function will be called again\n")
        time.sleep(100)
        query_site(url, params, fmt=JSON)
    '''
    if r.status_code == requests.codes.ok:
        return {
            JSON: __get_json,
            HTML: __get_html
        }[fmt](r)
    else:
        print("Request limit reached!\n")
        sys.exit(0)
    '''

def __get_json(response):
    return response.json()


def __get_html(response):
    return BeautifulSoup(response.text, "html.parser")
