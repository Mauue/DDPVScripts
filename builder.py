import argparse

import networkx as nx
import matplotlib.pyplot as plt
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from pydot import Dot


class Planner:

    def __init__(self):
        self.edges = []
        self.graph = None
        self.nodes = []
        self.dvnet_nodes = {}
        self.node_nums = {}
        self.port_link = {}
        self.ports = {}

    def add_topologies(self, edges):
        for edge in edges:
            self.add_topology(edge)

    def add_topology(self, edge):
        d1 = edge[0]
        d2 = edge[1]
        self.add_port(d1, d1+"->"+d2, d2, d2+"->"+d1)
        # self.edges.append(edge)

    def add_port(self, device1, port1, device2, port2):
        device1 = device1.strip()
        port1 = port1.strip()
        device2 = device2.strip()
        port2 = port2.strip()
        self.ports.setdefault(device1, {})
        self.ports[device1].setdefault(device2, [])
        self.ports.setdefault(device2, {})
        self.ports[device2].setdefault(device1, [])
        p1 = Port(device1, port1)
        p2 = Port(device2, port2)
        p1.link(p2)
        self.port_link[p1] = p2
        self.port_link[p2] = p1
        self.ports[device1][device2].append(p1)
        self.ports[device2][device1].append(p2)
        self.edges.append((device1, device2))

    def build(self):
        G = nx.Graph()
        G.add_edges_from(self.edges)
        self.graph = G
        self.nodes = list(G.nodes)

    def gen_path(self, src, dst, addition_cost):
        try:
            l = nx.shortest_path(self.graph, src, dst)
        except nx.exception.NetworkXNoPath:
            return []
        return nx.all_simple_paths(self.graph, src, dst, cutoff=len(l)-1+addition_cost)

    def gen_dfa(self, path_list, dst):
        nodes = set(self.nodes)
        num = dict.fromkeys(nodes, 0)
        transitions = {"root": {}, dst: {}}
        states = {"root", dst}
        for i in path_list:
            last = "root"
            for item in i:
                transitions[last].setdefault(item, [])
                if item == dst:
                    transitions[last][item].append(dst)
                    continue
                now = str(item) + str(num[item])
                states.add(now)
                transitions.setdefault(now, {})
                transitions[last][item].append(now)
                num[item] += 1
                last = now
        final_states = set()
        final_states.add(dst)
        nfa = NFA(
            states=states,
            input_symbols=nodes,
            transitions=transitions,
            initial_state='root',
            final_states=final_states,
        )
        dfa = DFA.from_nfa(nfa)
        dfa2 = DFA(
            states=dfa.states, input_symbols=dfa.input_symbols, transitions=dfa.transitions,
            initial_state=dfa.initial_state, final_states=dfa.final_states, allow_partial=True
        )
        dfa2.minify(retain_names=False)
        return dfa2.transitions

    def convert_transitions_to_dvnet(self, transitions: dict):
        node_dict = {'root': "root-0"}
        if len(self.node_nums) == 0:
            self.node_nums = {}.fromkeys(self.nodes, 0)
        for node, t in transitions.items():
            for label, dst in t.items():
                src = node.strip('"{}')
                dst = dst.strip('"{}')
                # label = i.get_attributes()['label']
                # print(src, dst, label)
                if dst == '':
                    continue
                if dst not in node_dict:
                    node_dict.setdefault(dst, label+"-"+str(self.node_nums[label]))
                    self.node_nums[label] += 1
                src = node_dict[src]
                dst = node_dict[dst]
                src_node = self.dvnet_nodes.setdefault(src, Node(src))
                dst_node = self.dvnet_nodes.setdefault(dst, Node(dst))
                src_node.next.add(dst_node)
                dst_node.prev.add(src_node)

    def add_requirement(self, src, dst, addition_cost):
        paths = self.gen_path(src, dst, addition_cost)
        return paths

    def all_pair_requirement(self, addition_cost):
        for dst in self.nodes:
            paths = []

            for src in self.nodes:
                if dst == src:
                    continue
                paths.extend(self.add_requirement(src, dst, addition_cost))
                # print(paths)
            dfa_transition = self.gen_dfa(paths, dst)
            self.convert_transitions_to_dvnet(dfa_transition)

            # plt.figure(figsize=[60, 48])
            # nx.draw(dg)
            # plt.show()

            # exit(0)

    def covert_dvnet(self):
        dg = nx.DiGraph()
        dg.add_node("root-0")
        dg.add_nodes_from(self.dvnet_nodes.keys())
        for i in self.dvnet_nodes.values():
            for p in i.next:
                dg.add_edge(i.get_name(), p.get_name())
        print(nx.is_directed_acyclic_graph(dg))
        # print(dg.edges)
        for i in self.dvnet_nodes.values():
            if i.name == "root":
                continue
            _prev = []
            for p in i.prev:
                if p.name == "root":
                    continue
                for port in self.ports[i.name][p.name]:
                    _prev.append(Node(port.name+"-"+p.index))
            i.prev = _prev
            _next = []
            for n in i.next:
                for port in self.ports[i.name][n.name]:
                    _next.append(Node(port.name+"-"+n.index))
            i.next = _next
        dg = nx.DiGraph()
        dg.add_node("root-0")
        dg.add_nodes_from(self.dvnet_nodes.keys())
        for i in self.dvnet_nodes.values():
            for p in i.next:
                dst = self.port_link[Port(i.name, p.name)]
                dg.add_edge(i.get_name(), dst+"-"+p.index)
        print(nx.is_directed_acyclic_graph(dg))


    def read_topology_file(self, filename):
        with open(filename, mode="r") as f:
            l = f.readline()
            while l:
                token = l.split(" ")
                self.add_port(token[0], token[1], token[2], token[3])
                l = f.readline()

    def write_to_file(self, filename):
        with open(filename, mode="w") as f:
            for i in self.dvnet_nodes.values():
                if i.name == "root":
                     continue
                f.write(
                    "link %s %s next " % (i.name, i.index)
                    + " ".join(["%s %s" % (i.name, i.index) for i in i.next])
                    + "\n")
                f.write(
                    "link %s %s prev " % (i.name, i.index)
                    + " ".join(["%s %s" % (i.name, i.index) for i in i.prev])
                    + "\n")


class Node:
    def __init__(self, name):
        token = name.rsplit("-", 1)
        self.name = token[0]
        self.index = token[1]
        self.prev = set()
        self.next = set()

    def __str__(self):
        return "%s-%s prev:%s, next:%s" % (self.name, self.index, [i.name+"-"+i.index for i in self.prev], [i.name+"-"+i.index for i in self.next])

    def get_name(self):
        return self.name + "-" + str(self.index)


class Port:
    def __init__(self, device, name):
        self.device = device
        self.name = name
        self.to = None

    def link(self, port):
        self.to = port
        port.to = self

    def __hash__(self):
        return hash(self.device+self.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="the input topology file")
    parser.add_argument("output", help="the output dvnet file")
    args = parser.parse_args()
    p = Planner()
    p.read_topology_file(args.input)
    p.build()
    p.all_pair_requirement(2)
    p.covert_dvnet()
    p.write_to_file(args.output)
