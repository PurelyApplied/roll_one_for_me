"""Various component classes for /u/roll_one_for_me, as well as the
primary RollOneForMe class."""

# Todo: set a maximum recursion depth.

from reddit_bot import MailHandling
from rofm_classes import RollOneStats
from rofm_request_handling import RequestProcessing

from archive.rofm_sentinel import Sentinel


class RollOneForMe(Sentinel, RequestProcessing, MailHandling):
    """/u/roll_one_for_me bot."""

    def beep_boop(self):
        pass

    def __init__(self, load_stats_filename=None):
        super(RollOneForMe, self).__init__()
        self.stats = RollOneStats(load_stats_filename)
        
    def __repr__(self):
        return "<RollOneForMe>"

    def act(self):
        self.act_as_sentinel()
        self.answer_mail()

    def answer_mail(self):
        new_mail = self.fetch_new_mail()
        for notification in new_mail:
            # Mark as read within this loop, upon reply.
            pass
