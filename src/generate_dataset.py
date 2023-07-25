import os
import re
import argparse
import pandas as pd
import datetime
import utils
import unicodedata

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

def rename_country(country):
    # this is needed to compare "türkiye"
    def g(x):
        return unicodedata.normalize('NFKD', x)

    t = {g("north_macedonia"): "north-macedonia", g("turkiye"): "turkey", g("türkiye"): "turkey", g("bosnia-and-herzegovina"): g("bosnia-herzegovina"), g("russian-federation"): "russia", g("republic-of-moldova"): "moldova"}
    if g(country) in t.keys():
        return t[g(country)]
    else:
        return country


def filter_rows(df):
    non_alpha_pattern = re.compile(r'\W')
    rows_to_drop = []
    rows_to_add = []
    for index, row in df.iterrows():
        s = row['sentence']
        # check if sentence is actaul a string
        if not isinstance(s, str):
            rows_to_drop.append(index)
            continue
        if not isinstance(row['country'], str):
            rows_to_drop.append(index)
            continue
        words = s.split()
        # remove short sentences
        if len(words) < 3:
            rows_to_drop.append(index)
            continue
        # check if a sentence is made up of enough words
        non_alpha = 0
        single_char_count = 0
        for word in words:
            if non_alpha_pattern.search(word):
                non_alpha += 1
            if len(word) == 1:
                single_char_count += 1
        # use a ratio of 0.7; seems to capture most cases.
        ratio_non_alpha = float(non_alpha / len(words))
        if ratio_non_alpha > 0.7:
            rows_to_drop.append(index)
            continue
        ratio_single_word_char = float(single_char_count / len(words))
        if ratio_single_word_char > 0.7:
            rows_to_drop.append(index)
            continue
        # merge same countries with different names
        row['country'] = rename_country(row['country'])
        # check to split long sentences further e.g. lists
        if len(words) > 100:
            # filter out sentences with too mnay non-english words
            ratio_non_english_words = float(utils.count_non_english_words(s) / len(words))
            if ratio_non_english_words > 0.5:
                rows_to_drop.append(index)
                continue
            rows_to_drop.append(index)
            items = utils.split_itemized_sentence(s)
            for item in items:
                # again remove short sentences
                if len(item.split()) < 3:
                    continue
                new_row = {}
                for key in row.keys():
                    new_row[key] = row[key]
                new_row['sentence'] = item
                rows_to_add.append(new_row)

    # create new DataFrame
    new_df = df.drop(rows_to_drop)
    extra_df = pd.DataFrame(rows_to_add)
    filtered_df = pd.concat([new_df, extra_df], ignore_index=True)
    return filtered_df


csv_files = find_csv_files(args.rootfolder)
df = combine_csv_files(csv_files)
filtered_df = filter_rows(df)
write_csv_file(filtered_df)

