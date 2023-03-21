import time
import sys

from Planner.dvnet import DVNet
from Planner.planner2 import Planner2
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
import heapq
import argparse


def path_to_dfa(paths: list[list[str]]):
    initial_state = "root"
    final_state = "end"
    states = {initial_state, final_state, "ERROR"}
    symbol = set()
    transitions = {initial_state: {}, final_state: {}, "ERROR": {}}
    symbol_num = {}
    for i, path in enumerate(paths):
        symbol.add(str(i))
        last = initial_state
        for j in path:
            symbol.add(j)
            state = j + str(symbol_num.setdefault(j, 0))
            symbol_num[j] += 1
            states.add(state)
            transitions.setdefault(last, {})[str(i)] = state
            transitions.setdefault(state, {})[j] = state
            last = state
        transitions.setdefault(last, {})[str(i)] = final_state

    print(states)
    print(symbol)
    for t in transitions:
        for s in symbol:
            transitions[t].setdefault(s, 'ERROR')
    print(transitions)

    dfa = DFA(states=states, input_symbols=symbol, transitions=transitions,
              initial_state=initial_state, final_states={final_state}, allow_partial=True)
    print(dfa.validate())
    dfa = dfa.minify()
    return dfa


def run(topology_path):
    planner = Planner2()
    planner.read_topology_file(topology_path)
    pairs = len(planner.devices) * (len(planner.devices) - 1)
    print(topology_path, len(planner.devices), pairs)

    # t = planner.all_pair_reachability(k=0, x=2, output=None)
    # print(t)

    for x in range(2, 3):
        for k in range(0, 3, 2):
            times = 1
            t = 0
            for i in range(times):
                t += planner.all_pair_reachability(k=k, x=x, output=None)
            print("x=%s, k=%s, time= %.2f ms, avg: %.2f ms" % (x, k, t / times, t / times / pairs))


def test():
    planner = Planner2()
    planner.add_topologies(
        (("S", "A"), ("A", "B"), ("A", "W"), ("B", "C"), ("B", "W"), ("C", "W"), ("C", "D"), ("D", "W")))
    # planner.add_device("X")
    planner.gen_dvnet("D", "S", 2, 2, "0.puml")
    # planner.all_pair_reachability(2, 0,None)


if __name__ == "__main__":
    # step 1: 输入拓扑和需求，生成自动机
    # topology_paths = ["/home/hcy/ddpv/distributed-dpv-network-config/i2/i2.topology",
    #                   "/home/hcy/ddpv/distributed-dpv-network-config/st/st.topology"]
    #
    # # print(t1)
    # for topology_path in topology_paths:
    #     run(topology_path)
    # if sys.argv[1] == "test":
    #     test()
    # else:
    #     run(sys.argv[1])
    topology_path = sys.argv[1]
    output = sys.argv[2]
    planner = Planner2()
    planner.read_topology_file(topology_path)
    planner.all_pair_reachability(k=0, x=2, output=output)

