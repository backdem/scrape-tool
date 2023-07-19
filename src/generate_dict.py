
import os
import argparse
import pandas as pd
import datetime
import json

parser = argparse.ArgumentParser(description='Combine sources into one dataset.')
parser.add_argument('--outputfile', nargs='?', default='./output.json',
                    help='output file name.')
parser.add_argument('--inputfile', nargs='?', default='./',
                    help='input file.')
args = parser.parse_args()
filename = args.inputfile
topics = []
empty_line_counter = 1


def new_topic(name):
    return {"name": name, "words": []}


if os.path.exists(filename):
    with open(filename, "r") as file:
        topic = None
        for l in file:
            # Process each line here
            if l.isspace():
                # topic ends
                empty_line_counter += 1
            else:
                line = l.strip().lower()
                if empty_line_counter > 0:
                    print(f"new topic: {line}")
                    # new section/topic
                    if (topic):
                        topics.append(topic)
                    topic = new_topic(line)
                    empty_line_counter = 0
                else:
                    topic["words"].append(line)

        topics.append(topic)
    with open(args.outputfile, "w") as file:
        json.dump(topics, file)
else:
    print(f"File '{filename}' does not exist.")
