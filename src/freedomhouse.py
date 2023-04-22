import os
import csv
import nltk
from bs4 import BeautifulSoup
import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from nltk.tokenize import sent_tokenize
nltk.download("punkt")


version = '0.0.3'


def get_version():
    return version


def get_country_data(country, year):
    url = 'http://freedomhouse.org/country/' + country.lower() + '/freedom-world/' + year
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}

    req = Request(url, headers=hdr)
    data = {}
    try:
        with urlopen(req) as response:
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            data['country'] = country.lower()
            data['year'] = year
            data['source'] = 'freedomhouse'
            data['url'] = url
            data['scraper'] = {'name': 'freedomhouse.py', 'version': version}
            data['accessed_on'] = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
            data['country_score'] = soup.find(class_='country-score').text
            data['contents'] = []
            tags = []
            tags_stack = []
            for item in soup.find_all(class_=['data-label', 'field-formatted-text']):
                if 'data-label' in item.get('class'):
                    tags.append(item.text)
                else:
                    if len(tags_stack) >= len(tags):
                        tags_stack = tags_stack[:len(tags_stack) - len(tags)]
                    new_tags = tags_stack + tags
                    record = {}
                    record['text'] = item.text.replace('\n', ' ')
                    record['tags'] = new_tags[-3:]
                    data['contents'].append(record)
                    tags = []
                    tags_stack = new_tags
    except HTTPError as e:
        print("HTTPError " + str(e.code) + " retrieving url: ", url)
        return None
    else:
        if len(data['contents']) == 0:
            print(f'''No content for country {country} year {year}.''')
        return data

def create_data_structure(data):
    rows = []
    for c in data['contents']:
        text = c['text']
        tags = c['tags']
        lines = text.splitlines()
        sentences = []
        for line in lines:
            sentences += nltk.sent_tokenize(line)
        for s in sentences:
            rows.append((s, tags, data['country'], data['year'], data['source']))
    return rows


def convert_to_csv(rows, output_dir="./data/freedomhouse/raw-csv/", overwrite=False):
    current_datetime_utc = datetime.datetime.utcnow()
    # convert the datetime object to ISO format with 'Z' indicating UTC timezone
    current_datetime_utc_iso = current_datetime_utc.replace(microsecond=0).isoformat() + 'Z'
    if len(rows) == 0:
        return (False, None, current_datetime_utc_iso, version)
    country = rows[0][2]
    year = rows[0][3]
    file_name = country + "_" + year + ".csv"
    output_file = os.path.join(output_dir, file_name)
    if os.path.exists(output_file) and overwrite is False:
        return (False, file_name, current_datetime_utc_iso, version)
    else:
        with open(output_file, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            header = ("sentence", "section", "country", "year", "source")
            writer.writerow(header)
            for row in rows:
                writer.writerow(row)
        return (True, file_name, current_datetime_utc_iso, version)
