import os
import argparse
import pandas as pd
import datetime

parser = argparse.ArgumentParser(description='Combine sources into one dataset.')
parser.add_argument('--outputfilename', nargs='?', default='./output.csv',
                    help='output file name.')
parser.add_argument('--rootfolder', nargs='?', default='./',
                    help='root folder with CSV data files.')
args = parser.parse_args()


def find_csv_files(root_dir):
    csv_files = []
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(subdir, file))
    return csv_files


def combine_csv_files(files):
    csvs = [pd.read_csv(file, dtype={'year': str}, comment="#") for file in files]
    data = pd.concat(csvs, ignore_index=True)
    return pd.DataFrame(data)


def write_csv_file(df):
    current_datetime_utc = datetime.datetime.utcnow()
    # convert the datetime object to ISO format with 'Z' indicating UTC timezone
    current_datetime_utc_iso = current_datetime_utc.replace(microsecond=0).isoformat() + 'Z'
    with open(args.outputfilename, 'w') as f:
        f.write(f"# Generated on {current_datetime_utc_iso}\n")
        df.to_csv(f, index=False)


csv_files = find_csv_files(args.rootfolder)
df = combine_csv_files(csv_files)
write_csv_file(df)
