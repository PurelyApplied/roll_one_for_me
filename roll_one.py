#!/usr/bin/python3
# For top-level comment scanning, you need to get submission's ID and call r.get_submission(url=None, id=ID).  Otherwise you only get the summoning comment (and perhaps the path to it)

# To add: Look for tables that are actual tables.
# Look for keyword ROLL in tables and scan for arbitrary depth
import string, random, time, praw, re, pickle, os
from pprint import pprint  #for debugging / live testing

def fdate():
    return "-".join(str(x) for x in time.gmtime()[:6])


# Stash for future project:
#   BtS = r.get_subreddit('DnDBehindTheScreen')
#   mods = BtS.get_moderators()
#   threes = [ mods[i:i+3] for i in range(0, len(mods), 3) ]

##################
# Some constants #
##################
_version="1.1.2"
_last_updated="2015-11-18"

_trash = string.punctuation + string.whitespace

_header_regex = "^[dD](\d+)(.*)"
_line_regex = "^\d+\s*(.*)"
_summons_regex = "u/roll_one_for_me"

_mentions_attempts = 10
_answer_attempts = 10

_sleep_on_error = 10
_sleep_between_checks = 60

_log_filename = "rofm.log"
_log = None
_log_dir = "./logs"

_trivial_passes_per_heartbeat = 30

def main(debug=False):
    '''main(debug=False)
    Logs into Reddit, looks for unanswered user mentions, and generates and posts replies'''
    log("Begin main()")
    if not os.path.exists(_log_dir) or not os.path.isdir(_log_dir):
        log("Creating log directory.")
        os.system('mkdir ./logs')
    while True:
        try:
            log("Signing into Reddit.")
            r = sign_in()
            trivial_passes_count = _trivial_passes_per_heartbeat - 1
            while True:
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
                            item.log()
                    else:
                        log("Mail is not summons or error.  Logging item.")
                        item.log()
                    item.origin.mark_as_read()
                    trivial_passes_count = 0
                trivial_passes_count += 1 if len(to_process) == 0 else 0
                if trivial_passes_count == _trivial_passes_per_heartbeat:
                    log("Heartbeat.  {} passes without incident (or first pass).".format(_trivial_passes_per_heartbeat))
                    trivial_passes_count = 0
                time.sleep(_sleep_between_checks)
        except Exception as e:
            log("Top level.  Executing full reset.  Error details to follow.")
            log("Error: {}".format(e))
            time.sleep(_sleep_on_error)

def BeepBoop():
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

def test():
    r = sign_in()
    # already, ignore = pickle.load(open(_pickle_filename, 'rb'))
    my_mail = list(r.get_unread(unset_has_mail=False))
    mentions = list(r.get_mentions())
    return r, my_mail, mentions

def get_post_text(post):
    '''Returns text to parse from either Comment or Submission'''
    if type(post) == praw.objects.Comment:
        return post.body
    elif type(post) == praw.objects.Submission:
        return post.selftext
    else:
        raise RuntimeError("Attempt to get post text from non-Comment / non-Submission post.")

####################

# A Request may refer to many TableSource objects
# A TableSource may contain many tables
# A table refers to many TableItems
# A TableItem may contain an inline subtable
# TODO: InlineTable should probably inherit from Table

# All items parse text in constructor

class Request:
    def __init__(self, praw_ref, r):
        self.origin = praw_ref
        self.reddit = r
        self.tables_sources = []
        self.outcome = None
        self.instance = None

        self.parse()

    def text(self):
        if type(self.origin) == praw.objects.Comment:
            return self.origin.body
        elif type(self.origin) == praw.objects.Submission:
            return self.origin.selftext
        else:
            return ""
        
    # determine params, identify targets
    def parse(self):
        # TODO(Parse params, change targets, pass to Table calls
        T = TableSource(self.origin.submission, "this thread's original post")
        if T.has_tables():
            self.tables_sources.append(T)
        top_level_comments = self.reddit.get_submission(None, self.origin.submission.id).comments
        for item in top_level_comments:
            T = TableSource(item, "[this]({}) comment by {}".format(item.permalink, item.author) )
            if T.has_tables():
                T.parse()
                self.tables_sources.append(T)
        
    def roll(self):
        instance = [TS.roll() for TS in self.tables_sources]
        instance = [x for x in instance if x]
        return "\n\n-----\n\n".join(instance)
        
    def reply(self, reply_text):
        self.origin.reply(reply_text)

    def is_summons(self):
        return re.search(_summons_regex, get_post_text(self.origin).lower())

    def log(self):
        filename = "{}/{}-{}.log".format(_log_dir, self.origin.author, self.origin.fullname)
        with open(filename, 'w') as f:
            f.write("Time    :  {}\n".format(fdate() ))
            f.write("Author  :  {}\n".format(self.origin.author))
            f.write("Link    :  {}\n".format(self.origin.permalink))
            f.write("Type    :  {}\n".format(type(self.origin)))
            try:
                f.write("Body    : (below)\n[Begin body]\n{}\n[End body]\n".format( get_post_text(self.origin)))
            except:
                f.write("Body    : Could not resolve message body.")
            f.write("\n")
            try:
                f.write("Submission title : {}\n".format(self.origin.submission.title))
                f.write("Submission body  : (below)\n[Begin selftext]\n{}\n[End selftext]\n".format(self.origin.submission.selftext))
            except:
                f.write("Submission: Could not resolve submission.")
        filename = filename.rstrip("log") + "pickle"
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    def describe_source(self):
        return "From [this]({}) post by user {}...".format(self.source.permalink, self.source.author)

    def __repr__(self):
        return "<Request from /u/{} in thread \"{}\">".format(self.origin.author, self.origin.submission.title)

class TableSource:
    def __init__(self, praw_ref, descriptor):
        self.source = praw_ref
        self.desc = descriptor
        self.tables = []

        self.parse()
        
    def __repr__(self):
        return "<TableSource from {}>".format(self.desc)


    def roll(self):
        instance = [T.roll() for T in self.tables]
        instance = [x for x in instance if x]
        if instance:
            ret = "From {}...\n\n".format(self.desc)
            for item in instance:
                ret += item.unpack()
            return ret
        return None

    def has_tables(self):
        return ( 0 < len(self.tables) )

    def parse(self):
        indices = []
        last_index = 0
        text = get_post_text(self.source)
        lines = text.split("\n")
        for line_num in range(len(lines)):
            l = lines[line_num]
            if re.search(_header_regex, l.strip(_trash)):
                indices.append(line_num)
        # TODO: if no headers found
        if len(indices) == 0:
            return None
        
        table_text = []
        for i in range(len(indices) -1):
            table_text.append("\n".join(lines[ indices[i]:indices[i+1] ]))
        table_text.append("\n".join(lines[ indices[-1]: ]))

        self.tables = [ Table(t) for t in table_text ]

class Table:
    '''Container for a single set of TableItem objects
    A single post will likely contain many Table objects'''
    def __init__(self, text):
        self.text = text
        self.die = None
        self.header = ""
        self.outcomes = []
        self.instance = None
        self.is_inline = False

        self.parse()

    def __repr__(self):
        return "<Table with header: {}>".format(self.text.split('\n')[0])

    def roll(self):
        try:
            c = random.randint(1, self.die)
            ind = c - 1
            R = TableRoll(d=self.die,
                          rolled=c,
                          head=self.header,
                          out=self.outcomes[ind])
            if len(self.outcomes) != self.die:
                R.error("Expected {} items found {}".format(self.die, len(self.outcomes)))
            return R
        # TODO: Handle errors more gracefully.
        except:
            return None

    def parse(self):
        lines = self.text.split('\n')
        head = lines.pop(0)
        head_match = re.search(_header_regex, head.strip(_trash))
        self.die = int(head_match.group(1))
        self.header = head_match.group(2)
        self.outcomes = [ TableItem(l) for l in lines if re.search(_line_regex, l.strip(_trash)) ]
 
class TableItem:
    '''This class allows simple handling of in-line subtables'''
    def __init__(self, text):
        self.text = text
        self.inline_table = None
        self.outcome = ""

        self.parse()

    def __repr__(self):
        return "<TableItem: {}{}>".format(self.outcome, "; has inline table" if self.inline_table else "")

    def parse(self):
        main_regex = re.search(_line_regex, self.text.strip(_trash))
        if not main_regex:
            return
        self.outcome = main_regex.group(1)
        if re.search("[dD]\d+", self.outcome):
            die_regex = re.search("[dD]\d+", self.outcome)
            self.inline_table = InlineTable(self.outcome[die_regex.start():])
            self.outcome = self.outcome[:die_regex.start()].strip(_trash)
        self.outcome = self.outcome.strip(_trash)

    def get(self):
        if self.inline_table:
            return self.outcome + self.inline_table.roll()
        else:
            return self.outcome
        
class InlineTable:
    def __init__(self, text):
        self.text = text
        self.die = None
        self.outcomes = []
        self.header = ""
        
        self.parse()

    def __repr__(self):
        return "<d{} Inline table>".format(self.die)

    def parse(self):
        top = re.search("[dD](\d+)", self.text)
        self.die = int(top.group(1))
        #subtable = self.text[top.end():]
        #slices = []
        # TODO
        for subroll in range(1, self.die):
            self.outcomes.append(TableItem("Subtable rolling temporarily disabled."))

    def roll(self):
        cast = random.randint(1, self.die)
        ind = cast - 1
        R = TableRoll(self.die, cast, "", self.outcomes[ind])
        if len(self.outcomes) != self.die:
            R.error("Inline table expected {} items found {}".format(self.die, len(self.outcomes)))
        return R

class TableRoll:
    def __init__(self, d, rolled, head, out, err=None):
        self.d = d
        self.rolled = rolled
        self.head = head
        self.out = out
        self.sub = out.inline_table
        self.sub_out = None
        self.err = err

        if self.sub:
            self.sob_out = self.sub.roll()
        
    def __repr__(self):
        return "<d{} TableRoll: {}>".format(self.d, self.head)

    def error(self, e):
        self.err = e

    def unpack(self):
        ret  = "{}...    \n".format(self.head.strip(_trash))
        ret += "(d{} -> {}) {}.    \n".format(self.d, self.rolled, self.out.outcome)
        if self.sub:
            #ret += str(self.sub.outcome)
            print("type=", type(self.sub))
            ret += "(Subtable d{} -> {}) *Inline table parsing temporarily disabled.*".format(self.sub.die, random.randint(1, self.sub.die))
        ret += "\n\n"
        return ret

class Logger:
    def __init__(self, log_directory, log_filename):
        self.log_filename = log_filename

class Core:
    pass

def log(s):
    if debug:
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
