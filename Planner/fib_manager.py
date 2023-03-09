import os.path
import os
import socket
import struct

import networkx as nx
import argparse

from functools import reduce


class IpGenerator():
    def __init__(self, prefix=24, base=167772160):
        self.prefix = prefix
        self.network = 0
        self.m = 1
        self.n = 1
        self.o = 1
        self.base = base

    def gen(self):
        ip = self.base + (self.network << (32 - self.prefix))
        self.network += 1
        return ip


def gen_fib(input, output, nprefix, prefix, requirement=None):
    FIBs = {}
    nodeToPrefix = {}
    ipGen = IpGenerator(prefix)
    G = nx.Graph()
    res = []
    for line in open(input):
        if '?' in line or 'None' in line:
            continue
        arr = line.split()
        latency = 0
        if len(arr) > 4:
            latency = int(arr[4])
        
        G.add_edge(arr[0], arr[2], portmap={arr[0]: arr[1], arr[2]: arr[3]}, latency=latency)

    for node in G.nodes:
        FIBs[node] = []
        nodeToPrefix[node] = []
        for i in range(nprefix):
            nodeToPrefix[node].append(ipGen.gen())
        # res[node] = dict()
        # res[node]["ip"] = nodeToPrefix[node]
    with open(os.path.join(output, "1.space"), 'w') as f:
        if requirement is not None:
            f.write('[requirement] %s\n' % requirement)
        for node, ips in nodeToPrefix.items():
            for ip in ips:
                f.write('%s %s %s\n' % (node, ip, prefix))
            # print(node, ips)

    for n in G.nodes:
        lengths, paths = nx.single_source_dijkstra(G, n, weight='latency')
        for (dst, path) in paths.items():
            if dst == n:
                continue
            for p in nodeToPrefix[dst]:
                FIBs[n].append('%s %s %s' % (p, prefix, G[n][path[1]]['portmap'][n]))
    path = os.path.join(output, "rule")
    if not os.path.exists(path):
        os.mkdir(path)
    for (sw, rules) in FIBs.items():
        res.append({"name": sw, "ip": [ch1(i)+"/"+str(prefix) for i in nodeToPrefix[sw]], "rule_num": len(rules)})
        with open(os.path.join(path, sw), 'w') as f:
            for rule in rules:
                f.write('fw %s\n' % rule)
    return res
    # print('#nodes: %d' % len(G.nodes))
    # print('#edges: %d' % len(G.edges))
    # print('FIB generate to %s with %d entries' % (output, len(G.nodes) * (len(G.nodes) - 1) * nprefix))


def ch1(num):
    return socket.inet_ntoa(struct.pack("!I", num))


def read_fib(path, device):
    res = []
    with open(os.path.join(path, device), mode="r") as f:
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            token = line.split(" ")
            if token[0] == "fw":
                index = len(res)
                match = ch1(int(token[1])) + "/" + token[2]
                action = "fwd(ALL, {%s})" % token[3]
                res.append({
                    "index": index,
                    "match": match,
                    "action": action}
                )
    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="The output format is: node ip prefix outport, read as \"a node has a rule ip/prefix that forward to outport\"")
    parser.add_argument("input", help="the input topology file")
    parser.add_argument("output", help="the output FIB file")
    parser.add_argument("-nprefix", type=int, default=1, help="the number of prefixes on each node, default=1")
    parser.add_argument("-prefix", type=int, default=24, help="the prefix for each address, default=24")
    args = parser.parse_args()
    gen_fib(args.input, args.output, args.nprefix, args.prefix)