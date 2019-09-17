import json

DATA_DIR = './data/'

def write(id, data):
    path = DATA_DIR + str(id) + '.json'

    with open(path, 'w+') as file:
        json.dump(data, file)
