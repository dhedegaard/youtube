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


def fetch_channel_info(channelid, parts=('snippet', 'contentDetails')):
    '''
    Fetches and returns a dict of info about a given channel, with the given
    channel id.
    '''
    resp = requests.get(
        'https://www.googleapis.com/youtube/v3/channels', params={
            'part': ','.join(parts),
            'id': channelid,
            'key': settings.YOUTUBE_API_KEY,
        }
    )
    resp.raise_for_status()
    return resp.json()['items'][0]


def fetch_videos_from_playlist(
        playlistid,
        parts=('contentDetails',),
        next_page_token=None):
    '''
    Fetches and returns a list of videoids from a playlist with a given
    playlistid as well as the next_page_token, if one is available as:
    -> (videos [list[dict]], next_page_token [string|None])

    If a next_page_token is supplied, it is submitted to the API as the
    pageToken parameter, returning videos after the ones on the first "page".
    '''
    # Fetch playlist-data from the API, without fetching extended info from the
    # API.
    resp = requests.get(
        'https://www.googleapis.com/youtube/v3/playlistItems', params={
            'part': ','.join(parts),
            'maxResults': 50,
            'playlistId': playlistid,
            'key': settings.YOUTUBE_API_KEY,
            'pageToken': next_page_token,
        }
    )
    resp.raise_for_status()
    data = resp.json()

    return data['items'], data.get('nextPageToken')


def fetch_videos(videoids, parts=('snippet', 'contentDetails', 'statistics')):
    '''
    Fetches and returns a dictlist of data, for the given iterable of videoids.
    '''
    resp = requests.get(
        'https://www.googleapis.com/youtube/v3/videos', params={
            'part': ','.join(parts),
            'id': ','.join(videoids),
            'key': settings.YOUTUBE_API_KEY,
        }
    )
    resp.raise_for_status()
    return resp.json()['items']
