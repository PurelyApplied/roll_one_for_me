#!/usr/bin/python3
# For top-level comment scanning, you need to get submission's ID and call r.get_submission(url=None, id=ID).  Otherwise you only get the summoning comment (and perhaps the path to it)

# To add: Look for tables that are actual tables.
# Look for keyword ROLL in tables and scan for arbitrary depth
from roll_one_classes import *
import time, praw, os

def fdate():
    return "-".join(str(x) for x in time.gmtime()[:6])

##################
# Some constants #
##################
_version="1.2.3"
_last_updated="2016-01-11"

_sleep_on_error = 10
_sleep_between_checks = 60

_log_filename = "rofm.log"
_log = None
_log_dir = "./logs"

_trivial_passes_per_heartbeat = 30

_seen_max_len = 50
_fetch_limit=25

def main(debug=False):
    '''main(debug=False)
    Logs into Reddit, looks for unanswered user mentions, and generates and posts replies'''
    log("Begin main()")
    if not os.path.exists(_log_dir) or not os.path.isdir(_log_dir):
        log("Creating log directory.")
        os.system('mkdir ./logs')
    seen_by_sentinel = []
    while True:
        try:
            log("Signing into Reddit.")
            r = sign_in()
            trivial_passes_count = _trivial_passes_per_heartbeat - 1
            while True:
                was_mail = process_mail(r)
                was_sub = scan_submissions(seen_by_sentinel, r)
                trivial_passes_count += 1 if not was_mail and not was_sub else 0
                if trivial_passes_count == _trivial_passes_per_heartbeat:
                    log("Heartbeat.  {} passes without incident (or first pass).".format(_trivial_passes_per_heartbeat))
                    trivial_passes_count = 0
                time.sleep(_sleep_between_checks)
                
        except Exception as e:
            log("Top level.  Executing full reset.  Error details to follow.")
            log("Error: {}".format(e))
            time.sleep(_sleep_on_error)

# Returns true if anything happened
def scan_submissions(seen, r):
    '''This function groups the following:
    * Get the newest submissions to /r/DnDBehindTheStreen
    * Attempt to parse the item as containing tables
    * If tables are detected, post a top-level comment requesting that table rolls be performed there for readability
    # * Update list of seen tables
    # * Prune seen tables list if large.
    '''
    try:
        keep_it_tidy_reply = ("It looks like this post has some tables that I might be able to parse.  " +
                              "To keep things tidy and not detract from actual discussion of these tables, please make your /u/roll_one_for_me requests as children to this comment." +
                              BeepBoop() )
        BtS = r.get_subreddit('DnDBehindTheScreen')
        new_subs = BtS.get_new(limit=_fetch_limit)
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
                        log("Adding organizational comment to thread with title: {}".format(TS.source.title))
                        saw_something_said_something = True

        # Prune list to max size
        seen[:] = seen[-_seen_max_len:]
        return saw_something_said_something
    except Exception as e:
        log("Error during submissions scan: {}".format(e))
        return False

def process_mail(r):
    '''Processes notifications.  Returns True if any item was processed.'''
    # log("Fetching unread mail.")
    my_mail = list(r.get_unread(unset_has_mail=False))
    to_process = [Request(x, r) for x in my_mail]
    # log("{} items found to process.".format(len(to_process)))
    for item in to_process:
        if item.is_summons():
            reply_text = item.roll()
            okay = True
            if not reply_text:
                reply_text = "I'm sorry, but I can't find anything that I know how to parse.\n\n"
                okay = False
            reply_text += BeepBoop()
            item.reply(reply_text)
            if okay:
                log("Successfully resolving request: /u/{} @ {}.".format(item.origin.author,
                                                                         item.origin.permalink))
            else:
                log("Questionably resolving request: /u/{} @ {}.".format(item.origin.author,
                                                                         item.origin.permalink))
                item.log(_log_dir)
        else:
            log("Mail is not summons or error.  Logging item.")
            item.log(_log_dir)
        item.origin.mark_as_read()

    return ( 0 < len(to_process))

def BeepBoop():
    '''Builds and returns reply footer "Beep Boop I'm a bot..."'''
    s = "\n\n-----\n\n"
    s += ("*Beep boop I'm a bot.  " +
          "You can find details about me at " + 
          "[this](https://www.reddit.com/r/DnDBehindTheScreen/comments/3rryc9/introducing_a_new_bot_uroll_one_for_me_for_all/) post.  " +
          "If it looks like I've gone off the rails and might be summoning SkyNet, let /u/PurelyApplied know, even though he sees all of these because of the mentions anyway.*" )
    s += "\n\n^(v{}; code base last updated {})".format(_version, _last_updated)
    return s

def sign_in():
    '''Sign in to reddit using PRAW; returns Reddit handle'''
    r = praw.Reddit('Generate an outcome for random tables, under the name /u/roll_one_for_me'
                    'Written and maintained by /u/PurelyApplied')
    # login info in praw.ini
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

def log(s):
    if debug:
        print("LOG>", s)
        return
    _log = open(_log_filename, 'a')
    _log.write("{} ; {}\n".format(time.ctime(), s))
    _log.flush()
    _log.close()
    
####################

debug = ("y" in input("Enable debugging?  ").lower() )
if __name__=="__main__":
    if 'y' in input("Run main?  ").lower():
        main()

