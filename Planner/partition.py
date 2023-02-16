import argparse

import networkx as nx
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

# from . import *
# from .DVNet import DVNet
from .planner import Planner
# from ._base import *


class PartitionPlanner(Planner):

    def __init__(self):
        super().__init__()
        self.graph = None
        self._areas = dict()  # type:dict[str, set[str]]
        self._device_to_area = dict()  # type:dict[str, str]
        self.key_nodes = set()

    def add_area(self, area_name, *devices):
        self._areas[area_name] = set(devices)
        for device in devices:
            if device in self._device_to_area and self._device_to_area[device] != area_name:
                print("%s has two area: %s %s" % (device, area_name, self._device_to_area[device]))
                continue
            self._device_to_area[device] = area_name
            self.devices.add(device)

    def build(self):
        for device in self.devices:
            if device not in self._device_to_area:
                print("undistributed area: " + device)
                return
        G = nx.Graph()
        G.add_edges_from(self.edges)
        self.graph = G

    def _add_port_link(self, device1, port1, device2, port2):
        super()._add_port_link(device1, port1, device2, port2)
        if self._device_to_area[device1] != self._device_to_area[device2]:
            self.key_nodes.add(device1)
            self.key_nodes.add(device2)

    def partition_requirement(self, src, dst):
        # 移出非必要的设备
        self.key_nodes.update((src, dst))
        remove_devices = self.devices.difference(self.key_nodes)
        self.devices = self.key_nodes

        for device in remove_devices:
            if device in self.ports:
                del(self.ports[device])
            self._areas[self._device_to_area[device]].remove(device)
            del(self._device_to_area[device])

        for ports in self.ports.values():
            for device in remove_devices:
                if device in ports:
                    del(ports[device])



    # 区域内全连接
        for area, devices in self._areas.items():
            for d1 in devices:
                for d2 in devices:
                    if d1 == d2:
                        continue
                    self.add_topology((d1, d2))

        self.build()
        result = dict()
        dvnet = self.single_reachability_requirement(src, dst)
        for node in dvnet.nodes.values():
            if node.name == "root":
                continue
            area = self._device_to_area[node.name]
            result.setdefault(area, []).append(node)

        for area in result:
            print(area, ": ")
            for node in result[area]:
                print(str(node))


