#!/usr/bin/env python3
from anytree import RenderTree

from rofm.classes.core.work.workload import WorkNode, WorkloadType
from rofm.classes.reddit.endpoint import Reddit, comment_contains_username

if __name__ == '__main__':
    Reddit.login()
    random_mention = next(mention for mention in Reddit.r.inbox.all() if comment_contains_username(mention))
    work = WorkNode(WorkloadType.username_mention, args=(random_mention,))
    work.do_all_work()
    print(RenderTree(work))
