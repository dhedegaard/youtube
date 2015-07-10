from django.conf import settings
import requests


def does_channel_author_exist(author):
    '''
    Checks to see if a given author exists.
    '''
    resp = requests.get(
        'https://www.googleapis.com/youtube/v3/channels', params={
            'part': 'id',
            'forUsername': author,
            'key': settings.YOUTUBE_API_KEY,
        })
    resp.raise_for_status()

    data = resp.json()
    return data['pageInfo']['totalResults'] > 0


def calculate_rating(like_count, dislike_count):
    '''
    Calculates an old-style rating from a like- and dislike-count. The rating
    is rounded to 1 decimal point.

    In case of div by zero, None is returned.
    '''
    try:
        return round(float(like_count) /
                     (float(like_count) + float(dislike_count)) * 5.0, 1)
    except ZeroDivisionError:
        return None
