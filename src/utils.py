import os
import csv
import nltk
import datetime
import pycountry
import re
import spacy
nlp = spacy.load("en_core_web_sm")

countries = [c.name.lower() if not hasattr(c, 'common_name') else c.common_name.lower() for c in pycountry.countries]


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


def split_itemized_sentence(text):
    text = text.replace('i.e.', 'iieeii')
    pattern = r'(\d+)\.(\d+)'
    replacement = r'\1DOT\2'
    text = re.sub(pattern, replacement, text)
    items = re.split(r'(?:\d+\.|[IVX]+\.|[ivx]+\.)', text)
    items = [item.strip() for item in items if item.strip()]
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
