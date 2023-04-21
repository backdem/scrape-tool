import nltk
import os
import csv

from striprtf.striprtf import rtf_to_text
from nltk.tokenize import sent_tokenize


nltk.download("punkt")

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

def convert_to_csv(file_path, output_dir="./data/bti/raw-csv/"):
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    c_n_y = file_name.split("_")
    country = c_n_y[0].lower()
    year = c_n_y[1].replace("BTI", "")
    output_file = os.path.join(output_dir, file_name + ".csv")
    sentences = get_rtf_as_sentences(path)
    rows = create_data_structure(sentences, country, year)
    with open(output_file, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        for row in rows:
            writer.writerow(row)



# test
path = "./data/bti/raw-rtf/Moldova_BTI2003.rtf"
convert_to_csv(path)

