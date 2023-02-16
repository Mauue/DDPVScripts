from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from ._base import *

_ROOT_NODE_NAME = "root"
_END_NODE_SUFFIX = "^end"


class DVNet:

    def __init__(self, devices, ports):
        self.devices = set(devices)
        self.node_index_dict = dict().fromkeys(self.devices, 0)
        self.accept_node = set()
        self.nodes = dict()  # type:dict[str, Node]
        self.ports = ports

    def gen_dfa(self, path_list) -> DFA:
        temp_node_index_dict = self.node_index_dict.copy()
        transitions = {_ROOT_NODE_NAME: {}}
        final_states = set()
        for path in path_list:
            last = _ROOT_NODE_NAME
            for index, item in enumerate(path):
                transitions[last].setdefault(item, [])
                now = "%s^%s" % (item, temp_node_index_dict[item])
                if index == len(path) - 1:
                    now = item + _END_NODE_SUFFIX
                    final_states.add(item + _END_NODE_SUFFIX)
                else:
                    temp_node_index_dict[item] += 1
                transitions[now] = {item: [now]}
                transitions[last][item].append(now)
                last = now
        nfa = NFA(states=set(transitions.keys()), input_symbols=self.devices, transitions=transitions,
                  initial_state=_ROOT_NODE_NAME, final_states=final_states)
        dfa = DFA.from_nfa(nfa).minify(retain_names=True)
        return dfa

    # 给节点编号
    def number_node(self, node) -> str:
        name = "%s^%s" % (node, self.node_index_dict[node])
        self.node_index_dict[node] += 1
        return name

    def gen_dvnet(self, dfa):
        transitions = dfa.transitions
        final_states = set()
        for state in dfa.final_states:
            final_states.add(state.strip('"{}'))
        node_dict = {'root': "root^0"}
        for node, nexthops in transitions.items():
            for next_hop, next_node in nexthops.items():
                edge_src = node.strip('"{}')
                edge_dst = next_node.strip('"{}')
                if edge_dst == '':
                    continue
                if edge_dst not in node_dict:
                    node_dict[edge_dst] = self.number_node(edge_dst.rsplit('^')[0])
                if edge_src not in node_dict:
                    node_dict[edge_src] = self.number_node(edge_src.rsplit('^')[0])
                edge_src = node_dict[edge_src]
                edge_dst = node_dict[edge_dst]
                if edge_dst in final_states:
                    self.accept_node.add(edge_dst)
                edge_src_node = self.nodes.setdefault(edge_src, Node(edge_src))
                edge_dst_node = self.nodes.setdefault(edge_dst, Node(edge_dst))
                Node.add_edge(edge_src_node, edge_dst_node)
        self.covert_dvnet()

    def covert_dvnet(self):
        for i in self.nodes.values():
            if i.name in ("root", "end"):
                continue
            _prev = []
            for p in i.prev:
                if p.name == "root" or p == i:
                    continue
                for port in self.ports[i.name][p.name]:
                    _prev.append(Node(port.name+"^"+p.index))
            i.prev = _prev
            _next = []
            for n in i.next:
                if n == i:
                    continue
                for port in self.ports[i.name][n.name]:
                    _next.append(Node(port.name+"^"+n.index))
            i.next = _next

    def write_to_file(self, filename, handle=None):
        res = []
        with open(filename, mode="w") as f:
            for i in self.nodes.values():
                if i.name == "root":
                    continue
                if i.name + '-' + i.index in self.accept_node:
                    s = "linka %s %s next %s" % (i.name, i.index, " ".join(["%s %s" % (i.name, i.index) for i in i.next]))
                    res.append(s)
                    f.write(s + "\n")
                else:
                    s = "link %s %s next %s" % (i.name, i.index, " ".join(["%s %s" % (i.name, i.index) for i in i.next]))
                    f.write(s + "\n")
                    res.append(s)
                f.write(
                    "link %s %s prev " % (i.name, i.index)
                    + " ".join(["%s %s" % (i.name, i.index) for i in i.prev])
                    + "\n")
        if handle is not None:
            handle({"type": "DVNet", "data": res})
