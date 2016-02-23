#!/usr/bin/env python3

import requests
import re
from ipaddress import ip_address, ip_network
from datetime import datetime


def get_api_resource(url: str) -> dict:
    try:
        r = requests.get(url)
        api = r.json()
        assert api['version'] == 1
    except requests.exceptions.RequestException as e:
        print(e)
        exit(1)

    return api

def get_nodes(url: str) -> dict:
    api = get_api_resource(url)

    return api['nodes']

def validate_hostname(hostname: str) -> bool:
    return bool(hostname_regex.match(hostname))

def map_hostnames_to_addresses(nodes, hostname_regex, subnet) -> dict:
	mapped_hostnames = {}

	for node in nodes.values():
		try:
			hostname = node['nodeinfo']['hostname']
			address = [
				address for address 
				in node['nodeinfo']['network']['addresses'] 
				if ip_address(address) in subnet
			][0]

			if not validate_hostname(hostname):
				continue

			mapped_hostnames[hostname] = address
		except AddressValueError:
			pass

	return mapped_hostnames


nodes = get_nodes('https://api.marburg.freifunk.net/nodes.json')
hostname_regex = re.compile(r'35\d{3}-[\w-]{1,}', re.IGNORECASE)
subnet = ip_network('2a06:4b00:1000::/64')

mapped_hostnames = map_hostnames_to_addresses(nodes, hostname_regex, subnet)
max_hostname_length = max(map(len, mapped_hostnames))

# lol
print(
	'''$ORIGIN nodes.marburg.link.
$TTL 1h
@{s: <{path_width}} IN SOA         altair.reis.asia. freifunk.hsmr.cc. (
{s: <{path_width}}                 {serial}      ; serial
{s: <{path_width}}                 2h              ; Refresh
{s: <{path_width}}                 30m             ; Retry
{s: <{path_width}}                 3w              ; Expire
{s: <{path_width}}                 1h )            ; Negative Cache TTL

@{s: <{path_width}} IN NS          altair.reis.asia.
@{s: <{path_width}} IN NS          wega.reis.asia.
@{s: <{path_width}} IN NS          arturo.reis.asia.
	'''.format(
		serial=datetime.utcnow().strftime('%Y%m%d%H'),
		s=' ',
		path_width=max_hostname_length + 6
	)
)

for hostname, address in sorted(mapped_hostnames.items()):
	print(
		'{hostname: <{path_width}} IN AAAA        {address}'.format(
			hostname=hostname,
			address=address,
			path_width=max_hostname_length + 7
		)
	)
	