from Planner.partition import PartitionPlanner

if __name__ == "__main__":
    planner = PartitionPlanner()
    planner.add_area("1", "A", "B")
    planner.add_area("2", "C", "D", "X", "Y")
    planner.add_area("3", "E", "F")
    planner.add_topologies(
        (("B", "C"), ("C", "D"), ("D", "E"), ("E", "F"), ("X", "Y"), ("C", "X"))
    )
    planner.partition_requirement("A", "F")