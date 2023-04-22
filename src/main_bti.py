import os
import glob
import argparse
import json
from bti import convert_to_csv


def main():
    parser = argparse.ArgumentParser(description='Parse bti country report.')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite output file.')
    parser.add_argument('--datafolder', nargs='?', default='./',
                        help='output folder for json files.')
    parser.add_argument('--outputfolder', nargs='?', default='./',
                        help='output folder for json files.')
    parser.add_argument('--configfile', nargs='?', default='config.json',
                        help='path of config file.')
    parser.add_argument('-c', '--countries', nargs='*',
                        help='name countries to process.')
    parser.add_argument('-y', '--years', nargs='*',
                        help='years of reports')
    parser.add_argument('--printoutput', action='store_false',
                        help='print output to terminal.')

    args = parser.parse_args()
    # config = {}
    # if args.countries and args.years:
    #    config['countries'] = args.countries
    #    config['years'] = args.years
    # else:
    #    with open(args.configfile) as file:
    #        config = json.loads(file.read())

    all_files = glob.glob(os.path.join(args.datafolder, '*'))
    for file in all_files:
        (done, file, time, ver) = convert_to_csv(file, args.outputfolder, overwrite=args.overwrite)
        if done:
            print(f"converted {file} with bti parser version {ver} at {time}.")


main()
