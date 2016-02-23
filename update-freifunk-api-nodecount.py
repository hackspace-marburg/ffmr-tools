#!/usr/bin/env python3

import sys
import os.path
import json
from collections import OrderedDict
from datetime import datetime

def get_nodelist_count(nodelist_location: str) -> int:
    with open(nodelist_location, 'r') as nodelist:
        nodes = [
            node['id'] for node
            in json.load(nodelist)['nodes']
            if node['status']['online']
        ]
        return len(nodes)

def get_freifunk_api(ffapi_location: str) -> OrderedDict:
    with open(ffapi_location, 'r') as ffapi:
        return json.load(ffapi, object_pairs_hook=OrderedDict)

def update_freifunk_api(ffapi_location: str, nodelist_location: str):
    ffapi_data = get_freifunk_api(ffapi_location)
    ffapi_data['state']['nodes'] = get_nodelist_count(nodelist_location)
    ffapi_data['state']['lastchange'] = datetime.utcnow().isoformat()

    with open(ffapi_location, 'w') as ffapi:
        json.dump(ffapi_data, ffapi, indent=2)


update_freifunk_api(
    os.path.join(sys.argv[1], 'freifunk-marburg.json'),  # first argument is basepath
    os.path.join(sys.argv[1], 'nodelist.json')
)
