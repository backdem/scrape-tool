import nltk
import os
import utils

from striprtf.striprtf import rtf_to_text
nltk.download("punkt")


def get_rtf_as_sentences(file_path):
    with open(file_path) as infile:
        content = infile.read()
        text = rtf_to_text(content, encoding="utf-8", errors="ignore")
        return utils.get_sentences(text)


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
        new_s = utils.filter_sentence(s)
        if not utils.is_a_sentence(new_s):
            continue
        # Create a 5 column data structure with (sentence, section, country, year, source)
        row = (new_s, current_heading, country, year, "bti")
        rows.append(row)
        line_counter += 1
    return rows


def get_country_year_from_file(file_path):
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    c_n_y = file_name.split("_")
    year = c_n_y.pop().replace("BTI", "")
    country = "_".join(c_n_y)
    return (country.lower(), year)
