import os
import argparse
import json
from eu_rule_of_law import create_data_structure
from utils import convert_to_csv
from utils import print_rows
from eu_rule_of_law import get_html_doc
from eu_rule_of_law import get_country_and_year_from_html


def main():
    parser = argparse.ArgumentParser(description='Parse freedomhouse country report.')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite output file.')
    parser.add_argument('--outputfolder', nargs='?', default='./',
                        help='output folder for json files.')
    parser.add_argument('--configfile', nargs='?', default='config.json',
                        help='path of config file.')
    parser.add_argument('-id', '--docid', nargs='+',
                        help='document id from 301 to 326')
    parser.add_argument('--printoutput', action='store_true',
                        help='print output to terminal.')

    args = parser.parse_args()
    config = {}
    ids = []
    if args.docid:
        ids += args.docid
    else:
        with open(args.configfile) as file:
            config = json.loads(file.read())
            ids = config["sources"]["euRuleOfLaw"]["docIds"]

    for id in ids:
        html = get_html_doc(id)
        (country, year) = get_country_and_year_from_html(html)
        if not (country and year):
            print("[error] with doc: ", id)
        rows = create_data_structure(html)
        if args.printoutput:
            print_rows(rows)
        else:
            (done, file, time) = convert_to_csv(rows, args.outputfolder, overwrite=args.overwrite, country=country, year=year)
            if done:
                print(f"converted {file} with eu-rule-of-law parser at {time}.")
            else:
                print(f"[error] converting {file} with at {time}.")

main()
