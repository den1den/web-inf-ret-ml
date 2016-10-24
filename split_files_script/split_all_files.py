import json
import os

from os import listdir

skip_dirs = {'elections-03-10-raw', 'elections-28-09-raw', 'elections-29-09-raw'}
root_dir = '/home/dennis/pCloudDrive/tweets/' + 'Tweet'

tweet_criteria = {'in_reply_to_status_id_str', 'quoted_status', 'extended_entities', 'extended_tweet'}

tweets_per_file_target = 400

ts = set()


def split(filepath):
    print("Reading in %s" % filepath)
    filename = os.path.basename(filepath)
    dirpath = os.path.dirname(filepath)
    if filename.endswith('.split.json'):
        return

    with open(filepath, 'r') as fp:
        raw_data = fp.read()
    for f in listdir(dirpath):
        if f.endswith('.split.json'):
            os.remove(os.path.join(dirpath, f))

    # if raw_data.startswith('{{"'):
    #     raw_data = raw_data[1:len(raw_data)]
    #     print("trimed { at front")
    # if raw_data.endswith('null}}'):
    #     raw_data = raw_data[0:len(raw_data) - 1]
    #     print("trimed } at end")

    data_array = raw_data.split('}{')
    if data_array[0].startswith('{"'):
        data_array[0] = data_array[0][1:len(data_array[0])]
    last_entry = data_array[len(data_array) - 1]
    if last_entry.endswith('}}'):
        data_array[len(data_array) - 1] = last_entry[0:len(last_entry) - 1]

    fi = 0
    file_contents = "[\n"
    el = ""
    for i in range(0, len(data_array)):
        el += data_array[i]
        json_el = '{' + el + '}'
        try:
            json.loads(json_el)
            el = ""
        except Exception as e:
            # print("RAW data first 50 chars: %s" % raw_data[0:50])
            # print("RAW data last  50 chars: %s" % raw_data[len(raw_data) - 50:len(raw_data)])
            print("\n Merging two indices around %s:" % i)
            for j in range(max(0, i - 1), min(len(data_array), i + 3)):
                print('  index %d: %s' % (j, data_array[j].replace('\n', '<<<<?newline>>>>')))
            # print("invalid JSON: %s" % (json_el,))
            el += "}{"
            continue

        if fi < tweets_per_file_target - 1:
            file_contents += json_el + ',\n'
            fi += 1
        elif fi >= tweets_per_file_target - 1:
            file_contents += json_el + '\n]'
            # file is full
            splitfilepath = os.path.join(dirpath, filename + '.' + str(int(i / tweets_per_file_target)) + '.split.txt')
            # with open(splitfilepath, mode='w+') as fp:
            #    fp.write(file_contents)
            file_contents = "[\n"
            fi = 0


def main():
    for dp, dn, fn in os.walk(root_dir):
        for tweet_filename in fn:
            filepath = os.path.join(dp, tweet_filename)
            dirname = os.path.basename(os.path.dirname(filepath))
            if dirname in skip_dirs:
                # skip
                continue
            split(filepath)


if __name__ == '__main__':
    main()
