FROM python:3.6
LABEL maintainer=dennis@dhedegaard.dk
EXPOSE 8000
ENV PORT 8080

COPY requirements-dev.txt requirements.txt requirements.prod.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt -r requirements.txt -r requirements.prod.txt

COPY . ./

RUN python manage.py test && \
  python manage.py collectstatic --noinput -c

CMD python manage.py migrate && \
  gunicorn youtube.wsgi
