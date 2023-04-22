import os
import argparse
import json
from freedomhouse import get_country_data
from freedomhouse import create_data_structure
from freedomhouse import convert_to_csv


def main():
    parser = argparse.ArgumentParser(description='Parse freedomhouse country report.')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite output file.')
    parser.add_argument('--outputfolder', nargs='?', default='./',
                        help='output folder for json files.')
    parser.add_argument('--configfile', nargs='?', default='config.json',
                        help='path of config file.')
    parser.add_argument('-c', '--countries', nargs='+',
                        help='name countries to process.')
    parser.add_argument('-y', '--years', nargs='+',
                        help='years of reports')
    parser.add_argument('--printoutput', action='store_false',
                        help='print output to terminal.')

    args = parser.parse_args()
    config = {}
    if args.countries and args.years:
        config['countries'] = args.countries
        config['years'] = args.years
    else:
        with open(args.configfile) as file:
            config = json.loads(file.read())

    for country in config['countries']:
        for year in config['years']:
            data = get_country_data(country, str(year))
            rows = create_data_structure(data)
            (done, file, time, ver) = convert_to_csv(rows, args.outputfolder, args.overwrite)
            if done:
                print(f"converted {file} with freedomhouse parser version {ver} at {time}.")
            else:
                if file:
                    print(f"[error] converting {file} with freedomhouse parser version {ver} at {time}.")
                else:
                    print(f"[error] processing country {data['country']} year {data['year']}.")


main()
