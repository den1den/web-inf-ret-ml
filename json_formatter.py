import json

with open('in.txt') as rf:
    data = json.load(rf)
with open('out.json', 'w') as wf:
    json.dump(data[0:100], wf, indent=2)
