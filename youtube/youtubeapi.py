from django.conf import settings
import requests


def fetch_channel_id_for_author(author):
    '''
    Checks to see if a given author exists.

    Returns None or channelid as a string.
    '''
    resp = requests.get(
        'https://www.googleapis.com/youtube/v3/channels', params={
            'part': 'id',
            'forUsername': author,
            'key': settings.YOUTUBE_API_KEY,
        })
    resp.raise_for_status()

    data = resp.json()
    if data['pageInfo']['totalResults'] > 0:
        return data['items'][0]['id']

def check_channel_id_exists(channelid):
    '''
    Checks to see if a given channelid string is a valid youtube channel id.

    Returns True/False.
    '''
    resp = requests.get(
        'https://www.googleapis.com/youtube/v3/channels', params={
            'part': 'id',
            'id': channelid,
            'key': settings.YOUTUBE_API_KEY,
        })
    resp.raise_for_status()

    data = resp.json()
    return data['pageInfo']['totalResults'] > 0


def fetch_videocategories(categoryids):
    '''
    Fetches and returns a dictlist of data for the categoryids.
    '''
    resp = requests.get(
        'https://www.googleapis.com/youtube/v3/videoCategories',
        params={
            'part': 'snippet',
            'id': ','.join([str(e) for e in categoryids]),
            'key': settings.YOUTUBE_API_KEY,
        })
    resp.raise_for_status()
    return resp.json()['items']