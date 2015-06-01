from os import environ
from datetime import date
from datetime import datetime
from requests import get
from calendar import Calendar

import records

DNZ_URL = 'http://api.digitalnz.org/v3/records/'
DNZ_KEY = environ.get('DNZ_KEY')

cache = {}


def get_metadata(record):
    """
    Calls DNZ's API to retrieve the metadata for a given record.
    """

    id = record['id']

    url = DNZ_URL + '{id}.json?api_key={key}'.format(id=id, key=DNZ_KEY)

    metadata = get(url).json()['record']
    metadata['hash'] = record['hash']

    return metadata


def get_calendar():
    """
    Generates a calendar structure for the current month.
    """

    year = date.today().year
    month = date.today().month

    return Calendar(0).monthdatescalendar(year, month)


def update_record_cache():
    """
    Fills the cache with values for the record of the day if necessary.
    """

    global cache
    today = date.today()

    if ('day' not in cache) or (today != cache['day']):
        print('Invalidating cache for ' + str(today))

        cache['day'] = today

        try:
            cache['record'] = records.get_record_by_date(cache['day'])
            cache['metadata'] = get_metadata(cache['record'])
        except StopIteration:
            cache['record'] = {
                'hash': 'nothing',
                'date': '3320-05-04'
            }
            cache['metadata'] = {
                'object_url': '',
                'large_thumbnail_url': '',
                'landing_url': '/',
                'display_content_partner': '',
                'title': 'Not much to show today'
            }

    return cache


def format_response(record, metadata):
    """
    Generates all variables that will be passed to the template.
    """

    day_date = datetime.strptime(record['date'], '%Y-%m-%d').date()

    if metadata['object_url'] is not None:
        image = metadata['object_url']
    else:
        image = metadata['large_thumbnail_url']

    return {
        'date': day_date,
        'record': {
            'image': image,
            'url': metadata['landing_url'],
            'author': metadata['display_content_partner'],
            'title': metadata['title'],
            'permalink': '/record/' + record['hash']
        },
        'calendar': get_calendar(),
    }


def format_error_response(error):
    """
    Generates all variables that will be passed to the error template.
    """

    return {
        'date': date.today(),
        'error': error,
        'calendar': get_calendar()
    }
