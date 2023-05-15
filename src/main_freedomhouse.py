import argparse
import json
from freedomhouse import get_country_data
from freedomhouse import create_data_structure
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
    if args.countries and args.years:
        config['countries'] = args.countries
        config['years'] = args.years
    else:
        with open(args.configfile) as file:
            config = json.loads(file.read())
            sources = config['sources']
            all_countries = []
            for source in sources.keys():
                all_countries += sources[source]['countries']
            all_countries = list(set(all_countries))
            config['countries'] = all_countries
            config['years'] = sources['freedomhouse']['years']

    for country in config['countries']:
        for year in config['years']:
            if not args.overwrite:
                if utils.report_exists(args.outputfolder, country, year):
                    print(f"[info] report exists for {country} year {year}, skipping.")
                    continue
            data = get_country_data(country, str(year))
            if not data:
                print(f"[error] processing country {country} year {year}.")
                continue
            rows = create_data_structure(data)
            (done, file, time) = utils.convert_to_csv(rows, args.outputfolder, overwrite=args.overwrite)
            if done:
                print(f"converted {file} with freedomhouse parser at {time}.")
            else:
                if file:
                    print(f"[error] converting {file} with freedomhouse parser at {time}.")
                else:
                    print(f"[error] processing country {data['country']} year {data['year']}.")


main()
