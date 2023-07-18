import nltk
from bs4 import BeautifulSoup
import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib import parse
import utils
nltk.download("punkt")


def get_country_data(country, year, url):
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
            print(f'opened url: {url}')
            html = response.read().decode(response.headers.get_content_charset())
            soup = BeautifulSoup(html, 'html.parser')
            data['country'] = country.lower()
            data['year'] = year
            data['url'] = url
            data['scraper'] = {'name': 'freedomhouse.py'}
            data['accessed_on'] = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
            data['country_score'] = soup.find(class_='country-score').text
            data['contents'] = []
            tags = []
            tags_stack = []
            for item in soup.find_all(class_=['data-label', 'field-formatted-text']):
                for anchor in item.find_all('a'):
                    anchor.decompose()
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


def create_data_structure(data, source):
    rows = []
    for c in data['contents']:
        text = c['text']
        tags = c['tags']
        sentences = utils.get_sentences(text)
        for s in sentences:
            if utils.is_a_sentence(s):
                rows.append((s, tags, data['country'], data['year'], source))
    return rows
