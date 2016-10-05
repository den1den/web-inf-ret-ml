#!/usr/bin/env python3
import json
import os

if not os.path.exists('json-out'):
    os.makedirs('json-out')
for file in os.listdir("."):
    if file[0:1] == "x":
        with open(file) as f:
            contents = f.read()
            contents = contents[0:(len(contents) - 2)]
            try:
                contents_obj = json.loads('[' + contents + ']')
            except ValueError as e:
                print("Error in file " + file)
                raise e
            print("load " + str(len(contents_obj)) + " objects")
            with open("json-out/" + file + '.json', 'w') as f2:
                json.dump(contents_obj, f2, indent=2)
print("Done")
