import fitz as PyMuPDF
import utils as utils
import pycountry
import os
import re

countries = [c.name.lower() for c in pycountry.countries]


def get_country_year_from_file(file_name):
    parts = os.path.basename(file_name).lower().split("-")
    pattern = r"\d{4}"
    country = None
    year = None
    for p in parts:
        if p in countries:
            country = p
        match_year = re.search(pattern, p)
        if match_year:
            year = match_year.group()
    return (country, year)


def convert_pdf_to_csv(file, output_dir, overwrite=False):
    (country, year) = get_country_year_from_file(file)
    if not (country and year):
        raise ValueError(f"could not determine country or year from file name {file}")
    file_bytes = open(file, "rb").read()
    text = get_text(file_bytes)
    sentences = utils.get_sentences(text)
    rows = utils.create_data_structure(sentences, country, year, "greco")
    return utils.convert_to_csv(rows, output_dir, overwrite=overwrite, country=country, year=year)


def get_text(data: bytes) -> str:
    with PyMuPDF.open(stream=data, filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
    return text

# test
# file_path = "./data/coe/Greco-AdHocRep(2019)2-FINAL-eng-Greece-PUBLIC.docx.pdf"
# r = convert_pdf_to_csv(file_path, "./data/greco/raw-csv/", True)
# print(r)
