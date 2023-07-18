import argparse
import fitz as PyMuPDF
import utils as utils
import pycountry
import os
import re

countries = [c.name.lower() for c in pycountry.countries]


def get_country_year_from_file(file_name):
    parts = os.path.basename(file_name).lower().split("_")
    pattern = r"\d{4}"
    country = parts[0].lower()
    year = None
    for p in parts:
        match_year = re.search(pattern, p)
        if match_year:
            year = match_year.group()
    if not year:
        year = '2022'
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
            text += page.get_text()
    return text


def convert_pdf_to_text(file):
    file_bytes = open(file, "rb").read()
    text = get_text(file_bytes)
    nt = text.replace('\n', '')
    return nt


def create_data_structure(file_path, country, year):
    rows = []
    text = convert_pdf_to_text(file_path)
    ss = utils.get_sentences2(text)
    for s in ss:
        rows.append((s.lower(), 'none', country, year, 'greco'))
    return rows


def main():
    parser = argparse.ArgumentParser(description='Parse GRECO country report.')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite output file.')
    parser.add_argument('--outputfolder', nargs='?', default='./',
                        help='output folder for csv files.')
    parser.add_argument('--inputfolder', nargs='?', default=None,
                        help='folder with pdf files.')

    args = parser.parse_args()
    if not args.inputfolder:
        print("[error] must provide --inputfolder with pdf reports.")
        return

    progress = {}
    for filename in os.listdir(args.inputfolder):
        file_path = os.path.join(args.inputfolder, filename)
        if os.path.isfile(file_path):
            country, year = get_country_year_from_file(filename)
            rows = create_data_structure(file_path, country, year)
            rows = rows[2:]
            key = str(country) + str(year)
            append = progress.get(key, False)
            (done, file, time) = utils.convert_to_csv(rows, args.outputfolder, overwrite=args.overwrite, country=country, year=year, append=append)
            progress[key] = True
            if done:
                print(f"converted {file} with greco parser at {time}.")
            else:
                print(f"[error] converting {country}/{year} with at {time}.")


main()
