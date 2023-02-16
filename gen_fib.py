import networkx as nx
import argparse
from functools import reduce

class IpGen():
    def __init__(self, prefix=24):
        self.prefix = prefix
        self.network = (1 << prefix) - 1
        self.m = 1
        self.n = 1
        self.o = 1

    def gen(self):
        ip = self.network << (32 - self.prefix)
        self.network -= 1
        return ip

def gen_fib(input, output, nprefix, prefix):
    FIBs = {}
    nodeToPrefix = {}
    ipGen = IpGen(prefix)
    G = nx.Graph()
    for line in open(input):
        if '?' in line or 'None' in line:
            continue
        arr = line.split()
        latency = 0
        if len(arr) > 4:
            latency = int(arr[4])
        
        G.add_edge(arr[0], arr[2], portmap={arr[0]: arr[1], arr[2]: arr[3]}, latency=latency)
        FIBs[arr[0]] = []
        FIBs[arr[2]] = []
        nodeToPrefix[arr[0]] = []
        nodeToPrefix[arr[2]] = []
        for i in range(nprefix):
            nodeToPrefix[arr[0]].append(ipGen.gen())
            nodeToPrefix[arr[2]].append(ipGen.gen())
    # with open(output, 'w') as f:
        # for node, ips in nodeToPrefix.items():
        #     for ip in ips:
        #         f.write('%s %s %s\n' % (node, ip, prefix))
        #     # print(node, ips)

    ipGen = IpGen(prefix)
    for n in G.nodes:
        lengths, paths = nx.single_source_dijkstra(G, n, weight='latency')
        for (dst, path) in paths.items():
            if dst == n:
                continue
            for p in nodeToPrefix[dst]:
                FIBs[n].append('%s %s %s' % (p, prefix, G[n][path[1]]['portmap'][n]))

    with open(output, 'w') as f:
        for (sw, rules) in FIBs.items():
            for rule in rules:
                f.write('%s %s\n' % (sw, rule))

    print('#nodes: %d' % len(G.nodes))
    print('#edges: %d' % len(G.edges))
    print('FIB generate to %s with %d entries' % (output, len(G.nodes) * (len(G.nodes) - 1) * nprefix))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="The output format is: node ip prefix outport, read as \"a node has a rule ip/prefix that forward to outport\"")
    parser.add_argument("input", help="the input topology file")
    parser.add_argument("output", help="the output FIB file")
    parser.add_argument("-nprefix", type=int, default=1, help="the number of prefixes on each node, default=1")
    parser.add_argument("-prefix", type=int, default=24, help="the prefix for each address, default=24")
    args = parser.parse_args()
    gen_fib(args.input, args.output, args.nprefix, args.prefix)