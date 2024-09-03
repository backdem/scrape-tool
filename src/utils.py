import os
import csv
import fitz as PyMuPDF
import nltk
from nltk.corpus import words
import datetime
import pycountry
import re
import spacy
import langid
nlp = spacy.load("en_core_web_sm")

nltk.download('punkt')
nltk.download('words')

countries = [c.name.lower() if not hasattr(c, 'common_name') else c.common_name.lower() for c in pycountry.countries] + [c.name.lower() for c in pycountry.countries] + ["venda", "kosovo", "yugoslavia", "ciskei", "madeira", "canary islands", "channel islands", "reunion", "syria", "st. kitts-nevis", "st. vincent and the grenadines", "british virgin islands", "iran", "russia", "falkland islands", "macedonia", "aimenia", "azeitaijan", "swaziland", "vojvodina", "united states virgin islands", "northern marianas", "turks and caicos", "transkei", "svalbard", "wallis and futuna islands", "melilla", "irian jaya", "faeroe islands", "zaire", "united states of america", "sao tome and príncipe", "st. lucia", "korea, north", "korea, south", "laos", "micronesia", "kyrgyz republic", "brunei", "burma (myanmar)", "cape verde", "czech republic", "bosnia-herzegovina", "nagorno-karabakh", "(serbia and montenegro)", "st. pierre and miquelon", "rapanui (easter island)", "st. helena and dependencies", "west bank", "transnistria", "tibet", "south ossetia", "são tomé and príncipe", "gaza strip", "gazastrip", "abkhazia", "indian kashmir", "pakistani kashmir", "somaliland", "east timor", "congo, democratic republic of (kinshasa)", "(kinshasa)", "congo, republic of (brazzaville)", "crimea", "coˆte d’ivoire", "côte d'lvoire", "ivory coast", "são tomé and prícipe", "sao tomé and príncipe", "west papua (irian jaya)", "st. helena and", "central african", "costs rica", "czechoslovakia", "yemen, north", "yemen, south", "marshall islands", "virgin islands", "marianas", "british virgin", "bophutatswana", "the west bank", "antilles", "andorra", "futuna islands", "miquelon", "reunion", "french southern", "cocos (keeling)", "vanautu", "rapanui (easter", "bermuda", "azores", "emirates", "union of soviet", "tobago", "sao tome", "st. vincent", "nevis (st. kitts-", "equatorial", "germany, west", "germany, east", "dominican", "burma", "antigua", "solomon", "kingdom", "the grenadines", "nevis"]

country_mappings = {
    "nevis": "saint kitts and nevis",
    "the grenadines": "saint vincent and the grenadines",
    "kingdom": "united kingdom",
    "solomon": "solomon islands",
    "central african": "central african republic",
    "costs rica": "costa rica",
    "equatorial": "equatorial guinea",
    "germany, west": "west germany",
    "germany, east": "east germany",
    "dominican": "dominican republic",
    "antigua": "antigua and barbuda",
    "virgin islands": "united states virgin islands",
    "palau (belau)": "palau",
    "belau": "palau",
    "marianas": "northen marianas",
    "st. helena and": "saint helena",
    "british virgin": "british virgin islands",
    "antilles": "netherland antilles",
    "the west bank": "west bank",
    "futuna islands": "wallis and futuna islands",
    "miquelon": "saint pierre and miquelon",
    "mayotte (mahore)": "mayotte",
    "french southern": "french southern and antarctic territories",
    "rapanui (easter": "rapa nui",
    "cocos (keeling)": "cocos islands",
    "yemen, south": "south yemen",
    "yemen, north": "north yemen",
    "united states": "usa",
    "emirates": "united arab emirates",
    "union of soviet": "ussr",
    "tobago": "trinidad and tobago",
    "sao tome": "são tomé and príncipe",
    "st. vincent": "saint vincent and the grenadines",
    "st. lucia": "saint lucia",
    "nevis (st. kitts-": "saint kitts and nevis",
    "korea, north": "north korea",
    "korea, south": "south korea",
    "new guinea": "papua new guinea"

}

max_country_len = max(len(c.split()) for c in countries)

def fix_country_name(name):
    n = name.lower().strip()
    if n in country_mappings:
        return country_mappings[n]
    else:
        return n

def is_country(text):
    if len(text.split(' ')) > 6:
        return False
    cleaned_text = text.lower().strip()
    if cleaned_text in countries:
        return True
    else:
        for word in cleaned_text.split(' '):
            if word in countries:
                return True
    return False
        

def extract_pdf_metadata(file_path):
    # Open the PDF file
    pdf_document = PyMuPDF.open(file_path)

    # Get document metadata
    metadata = pdf_document.metadata

    # Close the PDF document
    pdf_document.close()
    return metadata

def extract_text_with_page_numbers(file_path):
    # Open the PDF file
    pdf_document = PyMuPDF.open(file_path)
    text_with_page_numbers = []

    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)
        text = page.get_text("text")
        text_with_page_numbers.append((page_number + 1, text))  # Add 1 to start page numbering from 1

    # Close the PDF document
    pdf_document.close()

    return text_with_page_numbers

def test_pdf_for_text(file_path, lang="en"):
    with PyMuPDF.open(file_path) as doc:
        for page in doc:
            text = page.get_text()
            detected_lang, _ = langid.classify(text)
            if detected_lang == lang:
                return True
    return False

def get_pdf_text(data: bytes) -> str:
    with PyMuPDF.open(stream=data, filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text


def create_folder_if_not_exists(folder_path):
      # Check if the folder already exists
      if not os.path.exists(folder_path):
          # Create the folder if it does not exist
          os.makedirs(folder_path)
          print(f"Folder '{folder_path}' created successfully.")


def get_year_from_text(text):
    pattern = r"\d{4}"
    year = None
    match_year = re.search(pattern, text)
    if match_year:
        year = match_year.group()
    return year

def get_sentences2(text):
    sentences = []
    doc = nlp(text)
    for sent in doc.sents:
        more_sents = split_itemized_sentence(sent.text)
        for s in more_sents:
            words = len(s.split(' '))
            if (words < 3):
                continue
            if '.....' in s:
                continue
            s = re.sub(r'^\d+', '', s)
            s = filter_sentence(s)
            sentences.append(s)
    return sentences

def get_sentences(text):
    text = text.replace('e.g.', 'eeggee')
    text = text.replace('e. g.', 'eeggee')
    text = text.replace('i. e.', 'iieeii')
    text = text.replace('i.e.', 'iieeii')

    sentences = []
    for line in text.splitlines():
        ss = nltk.sent_tokenize(line)
        sentences += ss
    for i in range(len(sentences)):
        sentences[i] = sentences[i].replace('eeggee', 'e.g.')
        sentences[i] = sentences[i].replace('iieeii', 'i.e.')
    return sentences


def count_non_english_words(sentence):
    english_word_set = set(words.words())
    words_in_sentence = nltk.word_tokenize(sentence.lower())

    non_english_count = 0
    for word in words_in_sentence:
        if word not in english_word_set:
            non_english_count += 1

    return non_english_count


def split_itemized_sentence(text):
    text = text.replace('i.e.', 'iieeii')
    pattern = r'(\d+)\.(\d+)'
    replacement = r'\1DOT\2'
    text = re.sub(pattern, replacement, text)
    items = re.split(r'(?:\d+\.|[IVX]+[.)]|[ivx]+[.)]|\([a-z]\)|\s*[a-z]\))', text)
    items = [item.strip() for item in items if item]
    items = [item.replace('iieeii', 'i.e.') for item in items]
    items = [item.replace('DOT', '.') for item in items]
    return items

def filter_sentence(s):
    s1 = s.replace('\n', ' ').replace('\r', '')
    s2 = re.sub(r'[^\w\s\-.!:;,?()]', ' ', s1)
    return re.sub(r'\s+', ' ', s2).strip()


def is_a_sentence(s):
    if not s:
        return False
    words = s.split()
    #sentence_endings = ['.', '?', ';', ':', '!']
    if len(words) < 2:
        return False
    if not words[0][0].isalpha():
        return False
    #if words[-1][-1] not in sentence_endings:
    #    return False
    return True


def print_rows(rows):
    for r in rows:
        print(r)


def extract_country(text):
    country = None
    for c in countries:
        if c in text.lower():
            country = c
    if country:
        return country
    # check hyphinated countries
    long_names = [c for c in countries if len(c) > 1]
    long_names = ['-'.join(c) for c in long_names] + ['_'.join(c) for c in long_names]
    for c in long_names:
        if c in text.lower():
            country = c
    return country


def extract_year(text):
    words = text.split()
    pattern = r"\d{4}"
    year = None
    for w in words:
        match_year = re.search(pattern, w)
        if match_year:
            year = match_year.group()
    return year


def report_exists(output_dir, country, year, type='csv'):
    file_name = country + "_" + str(year) + "." + type
    output_file = os.path.join(output_dir, file_name)
    if os.path.exists(output_file):
        return True
    return False


def convert_to_csv(rows, output_dir=None, overwrite=False, country=None, year=None, append=False):
    if not output_dir:
        raise TypeError("parameters can not be None")
    current_datetime_utc = datetime.datetime.utcnow()
    # convert the datetime object to ISO format with 'Z' indicating UTC timezone
    current_datetime_utc_iso = current_datetime_utc.replace(microsecond=0).isoformat() + 'Z'
    if len(rows) == 0:
        return (False, None, current_datetime_utc_iso)

    if not country:
        country = rows[0][2]
    if not year:
        year = rows[0][3]

    file_name = country + "_" + year + ".csv"
    output_file = os.path.join(output_dir, file_name)
    if os.path.exists(output_file) and overwrite is False:
        return (False, file_name, current_datetime_utc_iso)
    else:
        mode = "a" if append else "w"
        with open(output_file, mode=mode, newline="") as csv_file:
            writer = csv.writer(csv_file)
            if not append:
                writer.writerow([f"# Generated on {current_datetime_utc_iso}"])
                header = ("sentence", "section", "country", "year", "source")
                writer.writerow(header)
            else:
                print(f"appending to {output_file}")
            for row in rows:
                writer.writerow(row)
        return (True, file_name, current_datetime_utc_iso)


def create_data_structure(sentences, country, year, source):
    rows = []
    current_heading = None
    line_counter = 0
    for s in sentences:
        row = ()
        words = s.split()
        first = words[0]
        last = words[-1]
        if (("\t" in s) and first[0].isdigit()):
            # Ignore numbered subsection heading
            continue
        if (len(words) == 1 and first[0].isdigit()):
            # Ignore numbered section item
            continue
        if (len(words) < 4 and last[-1].isalpha()):
            # Any sentence with less than 4 words and does not end with punctuation
            # we assume is a section title and add it as a tag to the sentence for better context.
            current_heading = s
            line_counter = 0
            continue
        # Create a 5 column data structure with (sentence, section, country, year, source)
        row = (s, current_heading.lower(), country, year, source)
        rows.append(row)
        line_counter += 1
    return rows
