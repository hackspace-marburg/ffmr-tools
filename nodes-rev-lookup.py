#!/usr/bin/env python

"""
Small script to search for nodes by a MAC address. This might ease understanding
the route within the network after `batctl traceroute`.
"""

import requests
import sys

from typing import Any, Dict, List, NamedTuple, Optional


NODES_JSON = "https://api.marburg.freifunk.net/nodes.json"


def get_nodes(url: str) -> Dict[str, Dict]:
    "Nodes section from the requested nodes.json file."
    r = requests.get(url)
    api = r.json()
    assert api["version"] == 1
    return api["nodes"]


class Node(NamedTuple):
    "Representation of a Node with its ID, hostname and path to the MAC."
    node_id: str
    hostname: str
    matches: List[str]

    def __repr__(self) -> str:
        return f"{self.hostname} ({self.node_id})"


def search_nodes(nodes: Dict[str, Dict], mac: str) -> List[Node]:
    "Search for Nodes by a MAC address."

    def search_rec(root: Dict[str, Any], path: str) -> List[str]:
        finds = []
        for k, v in root.items():
            if isinstance(v, dict):
                finds.extend(search_rec(v, path + "/" + k))
            elif isinstance(v, list) and mac in v:
                finds.append(path + "/" + k)
            elif v == mac:
                finds.append(path + "/" + k)
        return finds

    matches = []
    for node in nodes.values():
        node_info = node["nodeinfo"]
        finds = search_rec(node_info["network"], "")

        if finds:
            matches.append(Node(node_info["node_id"], node_info["hostname"], finds))
    return matches


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} MAC [MAC...]")
        sys.exit(1)

    nodes = get_nodes(NODES_JSON)
    for mac in sys.argv[1:]:
        print(f"{mac}: {search_nodes(nodes, mac)}")
