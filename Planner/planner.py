import argparse

import networkx as nx
from .dvnet import DVNet
from ._base import *


class Planner:

    def __init__(self):
        self.edges = []
        self.graph = None
        self.devices = set()
        self.dvnet_nodes = {}
        self.node_nums = {}
        self.port_link = {}
        self.ports = {}  # type:dict[str, dict[str, set[Port]]]
        self.accept_node = set()
        self.dvnet = None

    def add_topologies(self, edges):
        for edge in edges:
            self.add_topology(edge)

    def add_topology(self, edge):
        d1 = edge[0]
        d2 = edge[1]
        self._add_port_link(d1, d2, d2, d1)
        # self.edges.append(edge)

    def _add_port_link(self, device1, port1, device2, port2):
        device1 = device1.strip()
        port1 = port1.strip()
        device2 = device2.strip()
        port2 = port2.strip()
        self.ports.setdefault(device1, {})
        self.ports[device1].setdefault(device2, set())
        self.ports.setdefault(device2, {})
        self.ports[device2].setdefault(device1, set())
        p1 = Port(device1, port1)
        p2 = Port(device2, port2)
        p1.link(p2)
        self.port_link[p1] = p2
        self.port_link[p2] = p1
        self.ports[device1][device2].add(p1)
        self.ports[device2][device1].add(p2)
        self.edges.append((device1, device2))

    def build(self):
        G = nx.Graph()
        G.add_edges_from(self.edges)
        self.graph = G
        self.devices = set(G.nodes)

    def gen_path(self, src, dst, addition_cost) -> list[list[str]]:
        if addition_cost < 0:
            addition_cost = 64
        try:
            l = nx.shortest_path(self.graph, src, dst)
        except nx.exception.NetworkXNoPath:
            return []
        return nx.all_simple_paths(self.graph, src, dst, cutoff=len(l)-1+addition_cost)

    def get_path(self, src, dst) -> list[list[str]]:
        try:
            return nx.shortest_path(self.graph, src, dst)
        except nx.exception.NetworkXNoPath:
            return []

    def single_reachability_requirement(self, src, dst, addition_cost=5) -> DVNet:
        self.build()
        dvnet = DVNet(self.devices, self.ports)
        dfa = dvnet.gen_dfa(self.gen_path(src, dst, addition_cost))
        dvnet.gen_dvnet(dfa)
        return dvnet

    def all_pair_reachability_requirement(self, addition_cost) -> DVNet:
        self.build()
        paths = []
        dvnet = DVNet(self.devices, self.ports)

        for dst in self.devices:
            for src in self.devices:
                if dst == src:
                    continue
                paths.extend(self.gen_path(src, dst, addition_cost))
        dfa = dvnet.gen_dfa(paths)
        dvnet.gen_dvnet(dfa)
        return dvnet

    def get_network_diameter(self) -> int:
        m = 0
        for dst in self.devices:
            for src in self.devices:
                path = self.get_path(src, dst)
                m = max(m, len(path)-1)
        return m

    def read_topology_file(self, filename):
        with open(filename, mode="r") as f:
            l = f.readline()
            while l:
                token = l.strip().split(" ")
                if len(token) == 4:
                    self._add_port_link(token[0], token[1], token[2], token[3])
                elif len(token) == 2:
                    self._add_port_link(token[0], token[0] + '->' + token[1], token[1], token[1] + '->' + token[0])
                else:
                    print(token + " can not parsed")
                l = f.readline()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="the input topology file")
    parser.add_argument("output", help="the output DVNet file")
    args = parser.parse_args()
    p = Planner()
    print("parse topology")
    p.read_topology_file(args.input)
    # p.add_topologies((("A", "B"), ("B", "C"), ("C", "A")))
    print("build topology")
    p.build()
    # print(p.get_network_diameter())
    print("build requirement")
    dvnet = p.all_pair_reachability_requirement(2)
    print("generate dvnet")
    # p.covert_dvnet()
    # print("save dbnet")
    dvnet.write_to_file(args.output)
    # p.write_to_file("test.dvnet")
