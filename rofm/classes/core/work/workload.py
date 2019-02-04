#!/usr/bin/env python3
"""These classes define the workload for a given request.
A single request will spawn a single Workload.
WorkItems will be processed and grow a WorkLog, which will be a tree consisting of each job executed,
   with possible children WorkLog items if a given WorkItem requires additional work.
E.g., the following will all be represented by a single WorkItem, each spawning the next in the tree.
* Initial request parsing
* Parsing of a particular text for table (such as the OP or comment itself)
* Identifying that rolls are needed for a table, such as a "wide table"
* Performing and saving the outcome of the roll of a given table within the wide table.

Because the WorkLog is a tree in structure, the final response can be aggregated by parents, e.g.,
the response will consist of paragraph-separated sections for each parsed zone,
each parsed zone will consist of the outcome for each table,
a particular wide-table might be formatted different, aggregating its children's results.

Work is not necessarily processed in order, since modularity is ideal and any information required by one WorkItem
should be specified by its parent.
"""
from random import randint

from anytree import LevelOrderIter, RenderTree, NodeMixin


class Workload:
    def __init__(self, n):
        self.n = n

    def do_work(self):
        return [1 for _ in range(self.n + 1) if randint(0, self.n) == 0]


class WorkloadNode(Workload, NodeMixin):
    def __init__(self, name=None, parent=None):
        self.parent = parent
        self.name = name
        super(WorkloadNode, self).__init__(self.depth)

    def __do_work(self):
        additional_work = self.do_work()
        for _ in additional_work:
            WorkloadNode(name=f"{randint(1, self.depth + 1)}", parent=self)

    def __repr__(self):
        return f"<WorkNode {self.name}>"

    def work(self):
        for node in LevelOrderIter(self):
            node.__do_work()


if __name__ == '__main__':
    root = WorkloadNode("root")
    root.work()
    print(RenderTree(root))
