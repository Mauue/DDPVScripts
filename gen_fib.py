import argparse

from Planner.fib_manager import gen_fib_plus

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="The output format is: node ip prefix outport, read as \"a node has a rule ip/prefix that forward to outport\"")
    parser.add_argument("input", help="the input topology file")
    parser.add_argument("output", help="the output FIB file")
    parser.add_argument("-nprefix", type=int, default=1, help="the number of prefixes on each node, default=1")
    parser.add_argument("-prefix", type=int, default=24, help="the prefix for each address, default=24")
    parser.add_argument("-layers", type=int, default=0, help="the overlapping layers")
    parser.add_argument("-decompose", type=int, default=0, help="each rule will be decomposed into 2^k rules")
    args = parser.parse_args()
    gen_fib_plus(args.input, args.output, args.nprefix, args.prefix, layers=args.layers, decompose=args.decompose)

