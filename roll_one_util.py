'''Contains roll_one_for_me utility functions:
logger(log_str, filename, dbg=False) -- log events
fdate() -- formatted date string
get_post_text(PRAW_reference) -- returns text of post ; depricated
'''

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
