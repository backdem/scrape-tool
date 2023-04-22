import nltk
import os
import datetime
import csv

from striprtf.striprtf import rtf_to_text
from nltk.tokenize import sent_tokenize
nltk.download("punkt")

VERSION = "0.0.1"

def get_rtf_as_sentences(file_path):
    sentences = []
    with open(file_path) as infile:
        content = infile.read()
        text = rtf_to_text(content, encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        for line in lines:
            sentences += nltk.sent_tokenize(line)
    return sentences

def create_data_structure(sentences, country, year):
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
        row = (s, current_heading, country, year, "bti")
        rows.append(row)
        line_counter += 1
    return rows

def convert_to_csv(file_path, output_dir="./data/bti/raw-csv/", overwrite=False):
    current_datetime_utc = datetime.datetime.utcnow()
    # convert the datetime object to ISO format with 'Z' indicating UTC timezone
    current_datetime_utc_iso = current_datetime_utc.replace(microsecond=0).isoformat() + 'Z'
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    c_n_y = file_name.split("_")
    country = c_n_y[0].lower()
    year = c_n_y[1].replace("BTI", "")
    output_file = os.path.join(output_dir, file_name + ".csv")
    if os.path.exists(output_file) and overwrite is False:
        return (False, os.path.basename(file_path), current_datetime_utc_iso, VERSION)
    else:
        sentences = get_rtf_as_sentences(file_path)
        rows = create_data_structure(sentences, country, year)
        with open(output_file, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            header = ("sentence", "section", "country", "year", "source")
            writer.writerow(header)
            for row in rows:
                writer.writerow(row)
        return (True, os.path.basename(file_path), current_datetime_utc_iso, VERSION)
