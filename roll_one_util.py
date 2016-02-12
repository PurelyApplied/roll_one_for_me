'''Contains roll_one_for_me utility functions'''

import string

# Used by both Request and TableSource ; should perhaps depricate this
# and give each class its own method
def get_post_text(post):
    '''Returns text to parse from either Comment or Submission'''
    if type(post) == praw.objects.Comment:
        return post.body
    elif type(post) == praw.objects.Submission:
        return post.selftext
    else:
        raise RuntimeError("Attempt to get post text from non-Comment / non-Submission post.")

def fdate():
    return "-".join(str(x) for x in time.gmtime()[:6])

def logger(log_str, filename, dbg=False):
    '''logger(log_str, filename, debug=False)
    Appends "[Date and time] ; [log_str] \\n" to file with name filename
    if debug=True, prints "LOG> [log_str]" instead.'''
    if dbg:
        print("LOG>", log_str)
        return
    f = open(filename, 'a')
    f.write("{} ; {}\n".format(time.ctime(), log_str))
    f.close()


def get_globals():
    '''Sets a host of globals, which should be phased out, but there it is.'''
    global _version, _last_updated
    _version="1.2.4"
    _last_updated="2016-02-11"

    global _sleep_on_error, _sleep_between_checks
    _sleep_on_error = 10
    _sleep_between_checks = 60

    global _log_filename, _log, _log_dir
    _log_filename = "rofm.log"
    _log = None
    _log_dir = "./logs"

    global _trivial_passes_per_heartbeat
    _trivial_passes_per_heartbeat = 30

    global _seen_max_len,  _fetch_limit
    _seen_max_len = 50
    _fetch_limit=25

    global _trash, _header_regex, _line_regex,  _summons_regex
    _trash = string.punctuation + string.whitespace
    _header_regex = "^(\d+)?[dD](\d+)(.*)"
    _line_regex = "^(\d+)(\s*-+\s*\d+)?(.*)"
    _summons_regex = "u/roll_one_for_me"
