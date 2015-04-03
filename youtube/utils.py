import requests


def does_channel_author_exist(author):
    '''
    Checks to see if a given author exists.
    '''
    resp = requests.get(
        'https://gdata.youtube.com/feeds/api/users/%s'
        '?v=2.1&alt=json' % author)

    return resp.status_code == 200
