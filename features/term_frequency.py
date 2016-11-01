import csv
import json
import os
from collections import OrderedDict

import math

from config.config import PROJECT_DIR
from inputoutput.input import get_tweets

df_filename = os.path.join(PROJECT_DIR, 'df_t.json')
idf_filename = os.path.join(PROJECT_DIR, 'idf_t.json')
idf_csv_filename = os.path.join(PROJECT_DIR, 'idf_t.csv')


def write_tf_to_file():
    documents = get_tweets()
    df = {}
    for doc in documents:
        for word in set(doc.get_keywords()):
            if word in df:
                df[word] += 1
            else:
                df[word] = 1

    # Print df
    sorted_df = OrderedDict(sorted(df.items()))
    json.dump(sorted_df, open(df_filename, '+w'), indent=1)

    # Print idf
    idf = {term: math.log(len(documents) / df_t) for (term, df_t) in df.items()}
    sorted_idf = OrderedDict(sorted(idf.items()))
    json.dump(sorted_idf, open(idf_filename, '+w'), indent=1)

    # Print idf to csv
    with open(idf_csv_filename, '+w', encoding='utf8', newline='\n') as fp:
        writer = csv.writer(fp, delimiter=';')
        writer.writerow(['term', 'idf_t'])
        for (term, idf_t) in sorted_idf.items():
            writer.writerow((term, str(idf_t).replace('.', ','), ))


def get_idf_map():
    with open(idf_filename, 'r') as fp:
        d = json.load(fp)
    return d
