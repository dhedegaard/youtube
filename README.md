# Youtube #

[![Build Status](https://travis-ci.org/dhedegaard/youtube.svg?branch=master)](https://travis-ci.org/dhedegaard/youtube)
[![Coverage Status](https://coveralls.io/repos/dhedegaard/youtube/badge.svg?branch=master)](https://coveralls.io/r/dhedegaard/youtube?branch=master)
[![Requirements Status](https://requires.io/github/dhedegaard/youtube/requirements.svg?branch=master)](https://requires.io/github/dhedegaard/youtube/requirements/?branch=master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/605a167cdcf04637be5ef0b97d1bc1f5)](https://www.codacy.com/app/dhedegaard/youtube?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dhedegaard/youtube&amp;utm_campaign=Badge_Grade)

A simple Django application for aggregating youtube channels.

A running example is available here: <https://ut.dhedegaard.dk/>

## How to get it running in development ##

1. Make sure you have Python 3.6+ installed.
1. Make a new virtual environment (optional):\
   `$ virtualenv venv && source venv/bin/activate`
1. Install the dependencies from `requirements.txt` and `requirements-dev.txt` by:\
   `$ pip install -r requirements.txt -r requirements-dev.txt`
1. Go into `settings.py` and set the `YOUTUBE_API_KEY` to something valid.
   - Go to: <https://console.developers.google.com/>
   - Enable the Youtube Data API
   - Generate an API key (more info: <https://developers.google.com/youtube/v3/getting-started>)
1. Run migrations:\
   `$ python manage.py migrate`
1. Create a user:\
   `$ python manage.py createsuperuser`
1. Run the devserver:\
   `$ python manage.py runserver`
1. Go to <http://127.0.0.1:8000/>
1. Login and start adding youtube channels.
1. Run the `update_channels` job periodically, to fetch new youtube videos:\
   `$ python manage.py update_channels`


## For production ##

The usual:

- Disable `DEBUG` in settings.
- Run using gunicorn, uWSGI or similar.
- Replace the default sqlite database with postgres or similar.
- Add the `update_channels` job to your crontab.
