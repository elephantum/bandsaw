import sys
import csv
import datetime
import re
import requests

CSV_NAME = 'data.csv'


def create_csv(writer):
    writer.writerow(['timestamp', 'skin_temp', 'air_temp', 'heartrate', 'steps', 'gsr', 'calories'])


def append_to_csv(writer, json):
    """Takes JSON and flattens into CSVs."""

    if 'endtime' not in json:
        return
    for i in range((json['endtime'] - json['starttime']) / json['interval']):
        unix_time_utc = json['starttime'] + i*json['interval']

        skin_temp = json['metrics']['skin_temp']['values'][i]
        air_temp = json['metrics']['air_temp']['values'][i]
        heartrate = json['metrics']['heartrate']['values'][i]
        steps = json['metrics']['steps']['values'][i]
        gsr = json['metrics']['gsr']['values'][i]
        calories = json['metrics']['calories']['values'][i]

        timestamp = datetime.datetime.fromtimestamp(unix_time_utc)
        writer.writerow([timestamp, skin_temp, air_temp, heartrate, steps, gsr, calories])


def get_user_id(session):
    """This won't work until logging into the site with a username and password is working properly."""
    js = session.get('https://app.mybasis.com/js/lib/basis_api.js').text
    m = re.search('ClientID:"(?P<user_id>[0-9a-f])"', js)
    if m is None:
        return None
    return m.group('user_id')


def get_data(user_id, start_date, end_date):
    delta = datetime.timedelta(days=1)
    d = start_date
    while d <= end_date:
        url = 'https://app.mybasis.com/api/v1/chart/{0}.json?summary=true&interval=60&units=ms&start_date={1}&start_offset=-10800&end_offset=10800&heartrate=true&steps=true&calories=true&gsr=true&skin_temp=true&air_temp=true&bodystates=true'.format(user_id, d.strftime('%Y-%m-%d'))
        print 'get url', url
        yield requests.get(url).json()
        d += delta


if __name__ == '__main__':
    with open(CSV_NAME, 'w+') as csv_file:
        writer = csv.writer(csv_file)
        create_csv(writer)

        user_id = file('userid.txt').read()

        for data in get_data(user_id, datetime.datetime(2013, 9, 9), datetime.datetime(2013, 9, 14)):
            append_to_csv(writer, data)
