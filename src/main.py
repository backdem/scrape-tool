import os
import argparse
import json
from freedomhouse import get_country_data


def main():
    parser = argparse.ArgumentParser(description='Parse freedomhouse country report.')
    parser.add_argument('--overwrite', action='store_false',
                        help='overwrite output file.')
    parser.add_argument('--outputfolder', nargs='?', default='./',
                        help='output folder for json files.')
    parser.add_argument('--configfile', nargs='?', default='config.json',
                        help='path of config file.')

    args = parser.parse_args()

    print(args.configfile)
    with open(args.configfile) as file:
        config = json.loads(file.read())

    for country in config['countries']:
        for year in config['years']:
            filename = 'freedomhouse_' + country + '_' + str(year) + '.json'
            filepath = os.path.join(args.outputfolder, filename)
            if os.path.exists(filepath) and args.overwrite:
                print("file already exists: ", filepath)
            else:
                data = get_country_data(country, str(year))
                if not data:
                    continue
                print("writing file: ", filepath)
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)


main()
