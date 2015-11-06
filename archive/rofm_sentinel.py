import logging

from archive.reddit_bot import RedditBot


####################
# This page: Sentinel functionality


class Sentinel(RedditBot):
    """Sentinel action for /u/roll_one_for_me.  Monitors
/r/DnDBehindTheScreen for posts with tables, and adds orgizational
thread to keep requests from cluttering top-level comments.
    """
    ####################
    # Class members and methods
    # These are class-members to allow more natural config-file setup
    fetch_limit = 50
    cache_limit = 100
    fetch_failures_allowed = 5

    @classmethod
    def set_fetch_limit(cls, new_fetch_limit):
        cls.fetch_limit = new_fetch_limit

    @classmethod
    def set_cache_limit(cls, new_cache_limit):
        cls.cache_limit = new_cache_limit

    @classmethod
    def set_cache_limit(cls, new_fail_limit):
        cls.fetch_failures_allowed = new_fail_limit

    ####################
    # Instance methods
    def __init__(self, *seen_posts):
        super(Sentinel, self).__init__()
        self.seen = list(seen_posts)
        self.fetch_failure_count = 0

    def __repr__(self):
        return "<Sentinel>"

    def fetch_new_subs(self):
        try:
            logging.debug("Fetching newest /r/DnDBehindTheScreen submissions")
            BtS = self.r.get_subreddit('DnDBehindTheScreen')
            # TODO(2016-11-15): Get a "last fetched" timestamp instead
            # of cachine the pointers.
            new_submissions = list(BtS.get_new(limit=Sentinel.fetch_limit))
            self.fetch_failure_count = 0
            return new_submissions
        except:
            logging.error("Fetching new posts failed...")
            self.fetch_failure_count += 1
            if self.fetch_failure_count >= Sentinel.fetch_failures_allowed:
                logging.critical("Allowed failures exceeded.  Raising error.")
                raise RuntimeError(
                    "Sentinel fetch failure limit ({}) reached.".format(
                        Sentinel.fetch_failures_allowed))
            else:
                logging.error("Will try again next cycle.")
                return None

    def sentinel_comment(self, beep_boop=True):
        '''Produce organizational comment text'''
        reply_text = (
            "It looks like this post has some tables!"
            "  To keep things tidy and not detract from actual discussion"
            " of these tables, please make your /u/roll_one_for_me requests"
            " as children to this comment.")
        if beep_boop:
            reply_text += "\n\n" + self.beep_boop()
        return reply_text

    def beep_boop(self):
        raise NotImplementedError(
            "BeepBoop needs to be obfuscated by RollOneforMe")

    def act_as_sentinel(self):
        '''This function groups the following:
        * Get the newest submissions to /r/DnDBehindTheStreen
        * Attempt to parse the item as containing tables
        * If tables are detected, post a top-level comment requesting that
        table rolls be performed there for readability
        # * Update list of seen tables
        # * Prune seen tables list if large.
        '''

        num_orgos_made = 0
        new_submissions = self.fetch_new_subs()
        for item in new_submissions:
            if item not in self.seen:
                logging.debug("Considering submission: {}".format(item.title))
                if TableSource(item.selftext):
                    try:
                        # Verify I have not already replied, but
                        # thread isn't in cache (like after reload)
                        top_level_authors = [com.author
                                             for com in item.comments]
                        if self.r.user not in top_level_authors:
                            #item.add_comment(self.sentinel_comment())
                            print("Not commenting on it.")
                            num_orgos_made += 1
                            logging.info(
                                "Organizational comment made to thread:"
                                " {}".format(TS.source.title))
                    except:
                        logging.error("Error in Sentinel checking.")
        # Prune list to max size
        self.seen = self.seen[-cache_limit:]
        return num_orgos_made
