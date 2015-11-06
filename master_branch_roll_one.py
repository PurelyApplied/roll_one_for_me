#!/usr/bin/python3

# Incoming messages will differentiate by type: Mentions are
# praw.objects.Comment.  PM will me praw.objects.Message.  (And OP
# items will be praw.objects.Submission)

# If a link is to a comment, get_submission resolves the OP with one
# comment (the actual comment linked), even if it is greater than one
# generation deep in comments.

# To add: Look for tables that are actual tables.
# Look for keyword ROLL in tables and scan for arbitrary depth

import logging
import os
import pickle
import re
import sys
import time

import praw

from classes.tables import Table
from classes.util import configuration
from classes.util.sanitize import simplify_reddit_links

try:
    full_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(full_path)
    os.chdir(root_dir)
except:
    pass

##################
# Some constants #
##################



def main(debug=False):
    '''main(debug=False)
    Logs into Reddit, looks for unanswered user mentions, and
    generates and posts replies

    '''
    # Initialize
    logging.debug("Begin main()")
    seen_by_sentinel = []
    # Core loop
    while True:
        try:
            logging.debug("Signing into Reddit.")
            r = sign_in()
            trivial_passes_count = _trivial_passes_per_heartbeat - 1
            while True:
                was_mail = process_mail(r)
                was_sub = scan_submissions(seen_by_sentinel, r)
                trivial_passes_count += 1 if not was_mail and not was_sub else 0
                if trivial_passes_count == _trivial_passes_per_heartbeat:
                    logging.debug(
                        "Heartbeat.  {} passes without incident (or first pass).".format(_trivial_passes_per_heartbeat))
                    trivial_passes_count = 0
                time.sleep(_sleep_between_checks)
        except Exception as e:
            logging.debug("Top level.  Allowing to die for cron to revive.")
            logging.debug("Error: {}".format(e))
            raise (e)
        # We would like to avoid large caching and delayed logging.
        sys.stdout.flush()


# Returns true if anything happened
def scan_submissions(seen, r):
    '''This function groups the following:
    * Get the newest submissions to /r/DnDBehindTheStreen
    * Attempt to parse the item as containing tables
    * If tables are detected, post a top-level comment requesting that
      table rolls be performed there for readability
    # * Update list of seen tables
    # * Prune seen tables list if large.

    '''
    try:
        keep_it_tidy_reply = (
            "It looks like this post has some tables I might be able to parse."
            "  To keep things tidy and not detract from actual discussion"
            " of these tables, please make your /u/roll_one_for_me requests"
            " as children to this comment." +
            beep_boop())
        BtS = r.get_subreddit('DnDBehindTheScreen')
        new_subs = BtS.get_new(limit=configuration.fetch_limit)
        saw_something_said_something = False
        for item in new_subs:
            TS = TableSource(item, "scan")
            if TS.tables:
                top_level_authors = [com.author for com in TS.source.comments]
                # Check if I have already replied
                if not TS.source in seen:
                    seen.append(TS.source)
                    if not r.user in top_level_authors:
                        item.add_comment(keep_it_tidy_reply)
                        logging.debug("Adding organizational comment to thread with title: {}".format(TS.source.title))
                        saw_something_said_something = True

        # Prune list to max size
        seen[:] = seen[-configuration.seen_max_len:]
        return saw_something_said_something
    except Exception as e:
        logging.debug("Error during submissions scan: {}".format(e))
        return False


# returns True if anything processed
def process_mail(r):
    '''Processes notifications.  Returns True if any item was processed.'''
    my_mail = list(r.get_unread(unset_has_mail=False))
    to_process = [Request(x, r) for x in my_mail]
    for item in to_process:
        if item.is_summons() or item.is_PM():
            reply_text = item.roll()
            okay = True
            if not reply_text:
                reply_text = ("I'm sorry, but I can't find anything"
                              " that I know how to parse.\n\n")
                okay = False
            reply_text += beep_boop()
            if len(reply_text) > 10000:
                addition = ("\n\n**This reply would exceed 10000 characters"
                            " and has been shortened.  Chaining replies is an"
                            " intended future feature.")
                clip_point = 10000 - len(addition) - len(beep_boop()) - 200
                reply_text = reply_text[:clip_point] + addition + beep_boop()
            item.reply(reply_text)
            logging.debug("{} resolving request: {}.".format(
                "Successfully" if okay else "Questionably", item))
            if not okay:
                item.log(configuration.log_dir)
        else:
            logging.debug("Mail is not summons or error.  Logging item.")
            item.log(configuration.log_dir)
        item.origin.mark_as_read()
    return (0 < len(to_process))


def beep_boop():
    s = "\n\n-----\n\n"
    s += ("*Beep boop I'm a bot.  " +
          "You can find usage and known issue details about me, as well as my source code, on " +
          "[GitHub](https://github.com/PurelyApplied/roll_one_for_me) page.  " +
          "I am maintained by /u/PurelyApplied.*\n\n"
          )
    s += "\n\n^(v{}; code base last updated {})".format(configuration.version, configuration.last_updated)
    return s


def sign_in() -> praw.Reddit:
    '''Sign in to reddit using PRAW; returns Reddit handle'''
    r = praw.Reddit(
        user_agent=(
            'Generate an outcome for random tables, under the name'
            '/u/roll_one_for_me. Written and maintained by /u/PurelyApplied'),
        site_name="roll_one")
    # login info in praw.ini.  TODO: OAuth2
    r.login(disable_warning=True)
    return r


def test(mens=True):
    '''test(return_mentions=True)
    if return_mentions, returns tuple (reddit_handle, list_of_all_mail, list_of_mentions)
    else, returns tuple (reddit_handle, list_of_all_mail, None)
    '''
    r = sign_in()
    my_mail = list(r.get_unread(unset_has_mail=False))
    if mens:
        mentions = list(r.get_mentions())
    else:
        mentions = None
    return r, my_mail, mentions


####################
# classes
'''Class definitions for the roll_one_for_me bot

A Request fetches the submission and top-level comments of the appropriate thread.
Each of these items become a TableSource.
A TableSource is parsed for Tables.
A Table contains many TableItems.
When a Table is rolled, the appropriate TableItems are identified.
These are then built into TableRoll objects for reporting.
'''


class Request:
    def __init__(self, praw_ref, r):
        self.origin = praw_ref
        self.reddit = r
        self.tables_sources = []
        self.outcome = None

        self._parse()

    def __repr__(self):
        return "<Request from >".format(str(self))

    def __str__(self):
        via = None
        if type(self.origin) == praw.objects.Comment:
            via = "mention in {}".format(self.origin.submission.title)
        elif type(self.origin) == praw.objects.Message:
            via = "private message"
        else:
            via = "a mystery!"
        return "/u/{} via {}".format(self.origin.author, via)

    def _parse(self):
        '''Fetches text of submission and top-level comments from thread
        containing this Request.  Builds a TableSource for each, and
        attempts to parse each for tables.

        '''
        # Default behavior: OP and top-level comments, as applicable

        # print("Parsing Request...", file=sys.stderr)
        if re.search("\[.*?\]\s*\(.*?\)", self.origin.body):
            # print("Adding links...", file=sys.stderr)
            self.get_link_sources()
        else:
            # print("Adding default set...", file=sys.stderr)
            self.get_default_sources()

    def _maybe_add_source(self, source, desc):
        """Looks at PRAW submission and adds it if tables can be found."""
        T = TableSource(source, desc)
        if T.has_tables():
            self.tables_sources.append(T)

    def get_link_sources(self):
        links = re.findall("\[.*?\]\s*\(.*?\)", self.origin.body)
        # print("Link set:", file=sys.stderr)
        # print("\n".join([str(l) for l in links]), file=sys.stderr)
        for item in links:
            desc, href = re.search("\[(.*?)\]\s*\((.*?)\)", item).groups()
            href = simplify_reddit_links(href)
            if "reddit.com" in href:
                logging.debug("Processing href: {}".format(href))
                self._maybe_add_source(
                    self.reddit.get_submission(href),
                    desc)

    def get_default_sources(self):
        '''Default sources are OP and top-level comments'''
        try:
            # Add OP
            self._maybe_add_source(self.origin.submission, "this thread's original post")
            # Add Top-level comments
            top_level_comments = self.reddit.get_submission(None, self.origin.submission.id).comments
            for item in top_level_comments:
                self._maybe_add_source(item, "[this]({}) comment by {}".format(item.permalink, item.author))
        except:
            logging.debug("Could not add default sources.  (PM without links?)")

    def roll(self):
        instance = [TS.roll() for TS in self.tables_sources]
        instance = [x for x in instance if x]
        return "\n\n-----\n\n".join(instance)

    def reply(self, reply_text):
        self.origin.reply(reply_text)

    def is_summons(self):
        return re.search(configuration.configuration.summons_regex, get_post_text(self.origin).lower())

    def is_PM(self):
        return type(self.origin) == praw.objects.Message

    def log(self, log_dir):
        filename = "{}/rofm-{}-{}.log".format(log_dir, self.origin.author, self.origin.fullname)
        with open(filename, 'w') as f:
            f.write("Time    :  {}\n".format(fdate()))
            f.write("Author  :  {}\n".format(self.origin.author))
            try:
                f.write("Link    :  {}\n".format(self.origin.permalink))
            except:
                f.write("Link    :  Unavailable (PM?)\n")
            f.write("Type    :  {}\n".format(type(self.origin)))
            try:
                f.write("Body    : (below)\n[Begin body]\n{}\n[End body]\n".format(get_post_text(self.origin)))
            except:
                f.write("Body    : Could not resolve message body.")
            f.write("\n")
            try:
                f.write("Submission title : {}\n".format(self.origin.submission.title))
                f.write("Submission body  : (below)\n[Begin selftext]\n{}\n[End selftext]\n".format(
                    self.origin.submission.selftext))
            except:
                f.write("Submission: Could not resolve submission.")
        filename = filename.rstrip("log") + "pickle"
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    # This function is unused, but may be useful in future logging
    def describe_source(self):
        return "From [this]({}) post by user {}...".format(self.source.permalink, self.source.author)


class TableSource:
    def __init__(self, praw_ref, descriptor):
        self.source = praw_ref
        self.desc = descriptor
        self.tables = []

        self._parse()

    def __repr__(self):
        return "<TableSource from {}>".format(self.desc)

    def roll(self):
        instance = [T.roll() for T in self.tables]
        # Prune failed rolls
        instance = [x for x in instance if x]
        if instance:
            ret = "From {}...\n\n".format(self.desc)
            for item in instance:
                ret += item.unpack()
            return ret
        return None

    def has_tables(self):
        return (0 < len(self.tables))

    def _parse(self):
        indices = []
        text = get_post_text(self.source)
        lines = text.split("\n")
        for line_num in range(len(lines)):
            l = lines[line_num]
            if re.search(configuration.configuration.header_regex, l.strip(configuration.trash)):
                indices.append(line_num)
        # TODO: if no headers found?
        if len(indices) == 0:
            return None

        table_text = []
        for i in range(len(indices) - 1):
            table_text.append("\n".join(lines[indices[i]:indices[i + 1]]))
        table_text.append("\n".join(lines[indices[-1]:]))

        self.tables = [Table(t) for t in table_text]


class TableSourceFromText(TableSource):
    def __init__(self, text, descriptor):
        self.text = text
        self.desc = descriptor
        self.tables = []

        self._parse()

    # This is nearly identical to TableSource._parse ; if this is ever
    # used outside of testing, it behooves me to make a single
    # unifying method
    def _parse(self):
        indices = []
        text = self.text
        lines = text.split("\n")
        for line_num in range(len(lines)):
            l = lines[line_num]
            if re.search(configuration.header_regex, l.strip(configuration.trash)):
                indices.append(line_num)
        if len(indices) == 0:
            return None
        table_text = []
        for i in range(len(indices) - 1):
            table_text.append("\n".join(lines[indices[i]:indices[i + 1]]))
        table_text.append("\n".join(lines[indices[-1]:]))
        self.tables = [Table(t) for t in table_text]



####################
## util
'''Contains roll_one_for_me utility functions'''


# Used by both Request and TableSource ; should perhaps depricate this
# and give each class its own method
def get_post_text(post):
    '''Returns text to parse from either Comment or Submission'''
    if type(post) == praw.objects.Comment:
        return post.body
    elif type(post) == praw.objects.Submission:
        return post.selftext
    else:
        logging.debug("Attempt to get post text from"
               " non-Comment / non-Submission post; returning empty string")
        return ""


def fdate():
    return "-".join(str(x) for x in time.gmtime()[:6])


####################
# Some testing items
_test_table = "https://www.reddit.com/r/DnDBehindTheScreen/comments/4aqi2l/fashion_and_style/"
_test_request = "https://www.reddit.com/r/DnDBehindTheScreen/comments/4aqi2l/fashion_and_style/d12wero"
T = "This has a d12 1 one 2 two 3 thr 4 fou 5-6 fiv/six 7 sev 8 eig 9 nin 10 ten 11 ele 12 twe"

if __name__ == "__main__":
    print("Current working directory:", os.getcwd())
    if len(sys.argv) > 1:
        main()
    elif 'y' in input("Run main? >> ").lower():
        main()
