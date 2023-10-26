import argparse
import utils as utils
import pycountry
import os
import re
import glob
import datetime

test_file = './data/sources/freedomhouse/raw-pdf/Freedom_in_the_World_1989-1990_complete_book.pdf'
test_file2 = './data/sources/freedomhouse/raw-pdf/Freedom_in_the_World_2016_complete_book.pdf'
pdf_folder = './data/sources/freedomhouse/raw-pdf'

        #'2014:2019': 'Political Rights Rating:',
search_term = {
        '1990:2003': 'Population:',
        '2004:2013': 'Political Rights:',
        '2014:2019': 'Freedom Status:',
        '2020:now': 'Freedom Status'
        }

end_pages = {
        1990: 313,
        1991: 452,
        1992: 575,
        1993: 625,
        1994: 676,
        1995: 677,
        1996: 535,
        1997: 576,
        1998: 596,
        1999: 550,
        2000: 585,
        2001: 652,
        2002: 725,
        2003: 695,
        2004: 715,
        2005: 780,
        2006: 876,
        2007: 986,
        2008: 864,
        2009: 881,
        2010: 800,
        2011: 817,
        2012: 826,
        2013: 844,
        2014: 836,
        2015: 831,
        2016: 856,
        2017: 658,
        2018: 1202,
        2019: 1335,
        2020: 1436
        }

start_year = 1990

def get_year_from_text(text):
    pattern = r"\d{4}"
    matches = re.finditer(pattern, text)
    last_match = None
    for match in matches:
        last_match = match
    return last_match.group()

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
    text = utils.get_pdf_text(file_bytes)
    sentences = utils.get_sentences(text)
    rows = utils.create_data_structure(sentences, country, year, "greco")
    return utils.convert_to_csv(rows, output_dir, overwrite=overwrite, country=country, year=year)

def convert_pdf_to_text(file):
    file_bytes = open(file, "rb").read()
    text = utils.get_pdf_text(file_bytes)
    nt = text.replace('\n', '')
    return nt


def create_data_structure(file_path, country, year):
    rows = []
    text = convert_pdf_to_text(file_path)
    ss = utils.get_sentences2(text)
    for s in ss:
        rows.append((s.lower(), 'none', country, year, 'greco'))
    return rows


def _main():
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


def main():
    # Create a dict of years and the search term to look for.
    year_key_map = {}
    current_year = datetime.date.today().year
    for k, v in search_term.items():
        start_end = k.split(":")
        if start_end[1] == 'now':
            start_end[1] = current_year
        all_years = set([year for year in range(int(start_end[0]), int(start_end[1]) + 1)])
        for year in all_years:
            year_key_map[year] = v

    # Get the list of pdf year reports downloaded by download script
    #pdf_files = glob.glob(os.path.join(pdf_folder, '*.pdf'))
    pdf_files = [test_file]
    countries = {}
    weird_char = chr(0xF0C8)
    corpuses = {}
    # Process each file
    for file in pdf_files:
        year = get_year_from_text(file)
        if int(year) < start_year:
            continue
        end_page = end_pages[int(year)]
        country_name = None
        if year_key_map.get(int(year)) is None:
            print(f'Skipping {file}')
            continue

        print(f'Processingg {file}')
        text_with_page_numbers = utils.extract_text_with_page_numbers(file)
        key_term = year_key_map[int(year)]
        for page_number, text in text_with_page_numbers:
            if page_number > end_page:
                break
            lines = text.splitlines()
            lastlines = []
            for line_no, line in enumerate(lines):
                if len(lastlines) > 120:
                    lastlines.pop()
                look_ahead = lines[line_no+1:(line_no+15)]
                lastlines = [line] + lastlines
                look_ahead_lines = lastlines + look_ahead
                if country_name:
                    corpuses[(country_name, year)].append(line)
                if key_term in line:
                    found = False
                    for index, lastline in enumerate(reversed(look_ahead_lines)):
                        # Strip out weird chars
                        lastline = re.sub(r'^o ', '', lastline)
                        lastline = re.sub(r'^r ', '', lastline)
                        lastline = lastline.replace(weird_char, "")\
                            .strip()
    
                        # Country names start with capital letter
                        #if len(lastline) == 0 or not lastline[0].isupper():
                        #    continue
                        # Filter false postives e.g. Capital: Kuwait City
                        if lastline.split(":")[0] == 'Capital':
                            continue
                        if utils.is_country(lastline):
                            # Already processed then skip
                            if not lastline in countries:
                                found = True
                                country_name = lastline
                                countries[country_name] = countries.get(country_name, 0) + 1
                                corpuses[(country_name, year)] = [line]
                                break
                            #else:
                            #    print(f'ALREADY {lastline}')
                    #if not found:
                    #    print(f'TRUE NEGATIVE? {page_number} {year} {[l for l in look_ahead_lines if len(l.split()) < 12]}')
                        #print(f'TRUE NEGATIVE? {page_number} {year} {len(lastlines)} {lastlines}')



    sorted_dict = dict(sorted(countries.items(), key=lambda item: item[1], reverse=True))
    for k, v in sorted_dict.items():
        print(f'{k} {v}')
    #for k, v in corpuses.items():
    #    print(k)
    #    print("-----")
    #    for l in v:
    #        print(l)
    #    print()
    #    print()

main()
