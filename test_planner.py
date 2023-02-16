import argparse
from Planner.planner import Planner

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