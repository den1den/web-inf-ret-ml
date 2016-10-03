import json

with open('elections.json') as rf:
    data = json.load(rf)
print("Read in OK")

# with open('elections-out.json', 'w') as wf:
#    json.dump(data[0:100], wf, indent=2)
