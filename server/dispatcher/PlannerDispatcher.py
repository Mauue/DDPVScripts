import os.path
import re
import socket
import struct
from concurrent.futures import ThreadPoolExecutor
from Planner.planner import Planner
# from .builder import Planner
from Planner.fib_manager import gen_fib

_dispatcher = None


def get_planner_dispatcher():
    global _dispatcher
    if _dispatcher is None:
        _dispatcher = PlannerDispatcher()
    return _dispatcher


class PlannerDispatcher:
    _FREE_STATE = "free"

    def __init__(self):
        self._pool = ThreadPoolExecutor(max_workers=1)
        self._state = PlannerDispatcher._FREE_STATE
        self.handle = None
        self._working = False

    def _set_state(self, state=_FREE_STATE):
        self._state = state
        # if self.handle is not None:
        #     self.handle(state)

    def get_state(self):
        return self._state

    def new_requirement(self, topology, out, requirement, handle=None):
        self._working = True
        if handle is not None:
            self.handle = handle

        future = self._pool.submit(self._new_requirement, topology, out, requirement)

        def get_result(future):
            res = future.result()
            if res is not None:
                print(res)
        future.add_done_callback(get_result)

    def _new_requirement(self, topology, out, requirement):
        p = Planner()
        self._set_state("parse topology")
        p.add_topologies(topology)
        write_topology(topology, out)
        self._set_state("build DVNet")
        addition_hops = int(requirement["addition_hops"])
        p.gen(
            out+"/DPVNet.puml",
             [requirement["source"]],
             requirement["source"],
             "(equal, (`%s`.*`%s`, (==shortest+%d)))" % (requirement["source"], requirement["destination"], addition_hops))
        # dvnet = p.single_reachability_requirement(requirement["source"], requirement["destination"], addition_cost=addition_hops)
        if self.handle:
            self.handle({"type": "DVNet", "data": self.get_DPVNet(out+"/DPVNet.puml")})
        # p.covert_dvnet()
        # self._set_state("save DVNet")
        # dvnet.write_to_file(out+"/1.DVNet", handle=self.handle)
        self._set_state("build fib")
        res = gen_fib(os.path.join(out, "topology"), out, 1, 24)
        self.handle({"type": "info", "data": res})
        self._working = False

    def get_DPVNet(self, filepath):
        res = []
        with open(filepath, mode="r") as f:
            with open(filepath, mode="r") as f:
                l = f.readline()
                while l:
                    if not (l.startswith("@") or l.startswith("'") or l.startswith("state") or l.startswith("}")):
                        src, dst_u = l.split("-->", 1)
                        dst, _ = dst_u.split(":", 1)
                        res.append((src, dst))
                    l = f.readline()
        return res

    def get_topology(self, filepath):
        res = list()
        with open(filepath, mode="r") as f:
            l = f.readline()
            while l:
                token = l.strip().split(" ")
                if len(token) == 4:
                    res.append([token[0], token[2]])
                elif len(token) == 2:
                    res.append([token[0], token[1]])
                l = f.readline()
        return res


def write_topology(edges, out):
    with open(os.path.join(out, "topology"), mode="w", encoding="utf-8") as f:
        for edge in edges:
            f.write("%s %s %s %s\n" % (edge[0], edge[1], edge[1], edge[0]))


def write_rule(path, device, rules):
    pattern = re.compile("fwd\((...), \{(.*?)\}")
    with open(os.path.join(path, device), mode="w", encoding="utf-8") as f:
        for rule in rules:
            match = rule["match"].split("/")
            ip = struct.unpack("!L", socket.inet_aton(match[0]))[0]
            prefix = int(match[1])
            fwd = re.match(pattern, rule["action"])
            typ = fwd[1]
            ports = fwd[2].split(",")
            if len(ports) < 1:
                typ = "fw"
            print("%s %s %s %s\n" % (typ, ip, prefix, " ".join([i.strip() for i in ports])))
            f.write("%s %s %s %s\n" % (typ, ip, prefix, " ".join([i.strip() for i in ports])))

