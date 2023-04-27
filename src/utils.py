import os
import csv
import nltk
import datetime
import pycountry
import re

countries = [c.name.lower() if not hasattr(c, 'common_name') else c.common_name.lower() for c in pycountry.countries]

def get_sentences(text):
    sentences = []
    for line in text.splitlines():
        ss = nltk.sent_tokenize(line)
        sentences += ss
    return sentences

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


def convert_to_csv(rows, output_dir=None, overwrite=False, country=None, year=None):
    if not (output_dir and country and year):
        raise TypeError("parameters can not be None")
    current_datetime_utc = datetime.datetime.utcnow()
    # convert the datetime object to ISO format with 'Z' indicating UTC timezone
    current_datetime_utc_iso = current_datetime_utc.replace(microsecond=0).isoformat() + 'Z'
    if len(rows) == 0:
        return (False, None, current_datetime_utc_iso)
    file_name = country + "_" + year + ".csv"
    output_file = os.path.join(output_dir, file_name)
    if os.path.exists(output_file) and overwrite is False:
        return (False, file_name, current_datetime_utc_iso)
    else:
        with open(output_file, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([f"# Generated on {current_datetime_utc_iso}"])
            header = ("sentence", "section", "country", "year", "source")
            writer.writerow(header)
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
