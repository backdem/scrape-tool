import os
import glob
import argparse
import json
from bti import convert_to_csv


def main():
    parser = argparse.ArgumentParser(description='Parse bti country report.')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite output file.')
    parser.add_argument('--check_files', action='store_true',
                        help='check that files in data folder exist in output folder as csv.')
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
    error_cnt = 0
    for file in all_files:
        if args.check_files:
            file_name = os.path.splitext(os.path.basename(file))[0]
            output_file = os.path.join(args.outputfolder, file_name + ".csv")
            if os.path.exists(output_file) is False:
                error_cnt += 1
                print(f"[error] file {output_file} does not exist")
        else:
            (done, file, time, ver) = convert_to_csv(file, args.outputfolder, overwrite=args.overwrite)
            if done:
                print(f"converted {file} with bti parser version {ver} at {time}.")
            else:
                print(f"[error] converting {file} with bti parser version {ver} at {time}.")
                error_cnt += 1
    if error_cnt == 0:
        print("all done.")


main()
