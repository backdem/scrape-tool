import argparse
import json
import os
from freedomhouse import get_country_data
from freedomhouse import create_data_structure
import urllib.parse
import utils


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
    urls = {}
    with open(args.configfile) as file:
        config = json.loads(file.read())
        sources = config['sources']
        all_countries = []
        for source in sources.keys():
            all_countries += sources[source]['countries']
        all_countries = list(set(all_countries))
        config['countries'] = all_countries
        config['years'] = sources['freedomhouse']['years']
        urls = sources['freedomhouse']['urls']

    if args.countries and args.years:
        config['countries'] = args.countries
        config['years'] = args.years

    for report_type in urls.keys():
        url = urls[report_type]
        for country in config['countries']:
            for year in config['years']:
                actual_url = url.replace("COUNTRY", urllib.parse.quote(country))
                actual_url = actual_url.replace("YEAR", str(year))
                outputfolder = os.path.join(args.outputfolder, report_type)
                utils.create_folder_if_not_exists(outputfolder)
                if not args.overwrite:
                    if utils.report_exists(outputfolder, country, year):
                        print(f"[info] report exists for {country} year {year}, skipping.")
                        continue
                data = get_country_data(country, str(year), actual_url)
                if not data:
                    print(f"[error] processing country {country} year {year}.")
                    continue
                source = "freedomhouse_" + report_type
                rows = create_data_structure(data, source)
                (done, file, time) = utils.convert_to_csv(rows, outputfolder, overwrite=args.overwrite)
                if done:
                    print(f"converted {file} with freedomhouse parser at {time}.")
                else:
                    if file:
                        print(f"[error] converting {file} with freedomhouse parser at {time}.")
                    else:
                        print(f"[error] processing country {data['country']} year {data['year']}.")


main()
