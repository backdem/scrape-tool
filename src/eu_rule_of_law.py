import re
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import utils

url_pattern = 'https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:52020SC0'
url_source = None


def filter_out_roman_numerals(text):
    pattern = r"\b[IVXLCDM]+\b"
    text_without_roman_numerals = re.sub(pattern, "", text)
    words = text_without_roman_numerals.split()
    clean_sentence = ""
    for word in words:
        clean_sentence += " "
        for c in word:
            if c.isalnum():
                clean_sentence += c
    return clean_sentence[1:].lower()


def get_country_and_year_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find(class_='Titreobjet_cp').text
    country = utils.extract_country(title)
    year = utils.extract_year(title)
    return (country, year)


def create_data_structure(html):
    if not html:
        raise TypeError("needs html text as parameter")
    country = None
    year = None
    rows = []
    current_section = "introduction"
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find(class_='Titreobjet_cp').text
    country = utils.extract_country(title)
    year = utils.extract_year(title)
    for item in soup.find_all(class_=['li', 'Normal']):
        if 'li' in item.get('class'):
            current_section = filter_out_roman_numerals(item.text)
        else:
            for anchor in item.find_all("a"):
                # remove anchor html tags
                anchor.decompose()
            # html text clean up since <br> are replaced with \n and sentences are broken.
            text = item.text.replace('\n', ' ').replace('\r', '')
            new_text = re.sub(r'\s+', ' ', text).strip()
            sentences = utils.get_sentences(new_text)
            for s in sentences:
                if len(s.split()) > 2:
                    rows.append((s.lower(), current_section, country, year, "eu_rule_of_law"))
    return rows


def get_html_doc(doc_no):
    url = url_pattern + str(doc_no)
    global url_source
    url_source = url
    html = None
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}

    req = Request(url, headers=hdr)
    try:
        with urlopen(req) as response:
            html = response.read()
    except HTTPError as e:
        print("HTTPError " + str(e.code) + " retrieving url: ", url)
        return None
    else:
        return html
