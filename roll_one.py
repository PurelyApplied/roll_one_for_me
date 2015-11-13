#!/usr/bin/python3
# For top-level comment scanning, you need to get submission's ID and call r.get_submission(url=None, id=ID).  Otherwise you only get the summoning comment (and perhaps the path to it)

# To add: Look for tables that are actual tables.
# Look for keyword ROLL in tables and scan for arbitrary depth
from pprint import pprint
import string, random, time, praw, re, pickle

def doc(func):
    print(func.__doc__)

# These exist for ease of testing.
debug = ("y" in input("Enable debugging?  ").lower() )

##################
# Some constants #
##################
# We will strip space and punctuation
_trash = string.punctuation + string.whitespace
_header_regex = "^[dD](\d+)\s+(.*)"
#_line_regex = "^(\d+)\.\s*(.*)"
_line_regex = "^(\d+)\s*(.*)"
_summons_regex = "u/roll_one_for_me"
_mentions_attempts = 10
_answer_attempts = 10
_sleep_on_error = 10
_sleep_between_checks = 60
_pickle_filename = "pickle.cache"
_log_filename = "rofm.log"
_log = None
_trivial_passes_per_heartbeat = 10

def log(s):
    global _log
    if not _log:
        if debug:
            return
        raise RuntimeError("Could not open log file.")
    _log.write("{} ; {}\n".format(time.ctime(), s))
    _log.flush()

def main(debug=False):
    '''main(debug=False)
    Logs into Reddit, looks for unanswered user mentions, and generates and posts replies'''
    global _log
    _log = open(_log_filename, 'a')
    log("Begin main()")
    try:
        unidentified = pickle.load(open(_pickle_filename, "rb"))
    except:
        unidentified = []
    L_unIDed = len(unidentified)
    while True:
        try:
            log("Signing into Reddit.")
            r = sign_in()
            trivial_passes_count = _trivial_passes_per_heartbeat - 1
            while True:
                # log("Fetching unread mail.")
                my_mail = list(r.get_unread(unset_has_mail=False))
                # log("Mail fetched.  Processing.")
                unIDed_tags = [y[0] for y in unidentified]
                to_process = [x for x in my_mail if x not in unIDed_tags]
                # log("{} items found to process.".format(len(to_process)))
                for item in to_process:
                    if is_summons(item):
                        log("Answering summons at {}.".format(item.permalink))
                        answer_summons(item, r)
                    else:
                        log("Mail is not summons.  Probably a reply?  Item at {}".format(item.permalink))
                        my_replies = list(r.get_comment_replies())
                        unidentified.append( (item, "Comment reply?") )
                if len(unidentified) > L_unIDed:
                    L_unIDed = len(unidentified)
                    log("Pickling unidentified items for future investigation.  Current count: {}.".format(L_unIDed) )
                    pickle.dump(unidentified, open(_pickle_filename, "wb"))
                if len(to_process) == 0:
                    trivial_passes_count += 1
                else:
                    trivial_passes_count = 0
                if trivial_passes_count == _trivial_passes_per_heartbeat:
                    log("Heartbeat.  {} passes without incident (or first pass).".format(_trivial_passes_per_heartbeat))
                    trivial_passes_count = 0
                time.sleep(_sleep_between_checks)
        except Exception as e:
            log("Top level.  Executing full reset.  Error details to follow.")
            log("Error: {}".format(e))
            time.sleep(_sleep_on_error)

def is_summons(item):
    return re.search(_summons_regex, item.body.lower())

def answer_summons(summons, r):
    attempt = 0
    success = False
    while attempt < _answer_attempts and not success:
        try:
            answers = get_answer(summons, r)
            text = build_reply(answers, r, summons)
            # TODO: Check if text is over post-length and chain replies
            summons.reply(text)
            success = True
            log("Comment answered.  Marking mail as read.")
            summons.mark_as_read()
        except Exception as e:
            log("Failed to answer comment.  Failure #{}.  Comment at {}.".format(attempt + 1, summons.permalink ))
            log("Error as follows: {}".format(e))
            time.sleep(_sleep_on_error)
            attempt += 1
    if not success:
        log("Final failure to answer comment at {}".format(summons.permalink ))
        ignore_list.append(summons)
        raise RuntimeError("Error during response generation.")

def build_reply(answers, r, summons):
    '''build_reply(answers, r, summons):
    Builds reply given a list of string tuples
    
    answers: A list of string tuples, (output, intro)
    r: praw.*.Reddit handle
    summons: Comment reference for reply, intended for error handling but currently unused'''
    s  = "I'm happy to roll these for you.\n\n"
    for out, intro in answers:
        s += intro + "\n" + out
        s += "-----\n\n"
    if not answers:
        s += "Unfortunately, I can't seem to find any tables in this original post or any top-level comments.  "
        s += "I'm sorry to have failed you.  My author has been notified.  Appropraite action will be taken.\n\n"
        s += "-----\n\n"
        #try:
        #    # May fail due to captcha
        #    r.send_message(recipient='PurelyApplied',
        #                   subject='roll_one_for_me failure; no tables',
        #                   message="Failed responce to [this]({}) summons.".format(summons.permalink))
    s += "^(*Beep boop I'm a bot.  If it looks like I've gone off the rails and might be summoning SkyNet, let /u/PurelyApplied know.*)"
    return s

def sign_in():
    '''Sign in to reddit using PRAW; returns Reddit handle'''
    r = praw.Reddit('Generate an outcome for random tables, under the name /u/roll_one_for_me'
                    'Written and maintained by /u/PurelyApplied')
    # login info in praw.ini
    r.login()
    return r

def describe_source(post, was_OP=False):
    desc = "the original post" if was_OP else "[this]({}) comment by {}".format(post.permalink, post.author)
    desc = "From some tables found in " + desc + "...\n"
    return desc

def get_answer(summons, r):
    '''def get_answer(summons, r):
    Given a comment summons, generates a responce string'''
    # Texts exist as a tuple of ( text, author, link )
    op_text = summons.submission.selftext
    children = r.get_submission(None, summons.submission.id).comments
    All_rolled = [ get_generator(txt)() for txt in [op_text] + [x.body for x in children]]
    ret = []
    if All_rolled[0]:
        ret = [ ( All_rolled[0], describe_source(summons.submission, was_OP=True) ) ]
    ret = ret + [ (All_rolled[i+1], describe_source(children[i], was_OP=False) ) for i in range(len(children)) if All_rolled[i+1]]
    return ret
    # TODO: Change this to return the trio of lists (head, dice, outcomes)
    #       That way it can generalize to parse top-level comments, too
    # gen = get_generator(op_text)

def get_generator(op_text):
    '''def get_generator(op_text):
    Returns generator function gen given OP text, such that gen() returns a string reply'''
    def gen(head_list, dice_list, result_list):
        assert len(head_list) == len(dice_list) == len(result_list), "Generator list length mismatch"
        def _gen():
            s = ''
            for i in range(len(head_list)):
                h = head_list[i]
                d = dice_list[i]
                r = random.randint(0, d-1)
                out = result_list[i][r][1].strip(_trash)
                out = out + determine_and_resolve_subroll(out)
                s += "{}...    \n(d{} -> {}:) {}\n\n".format(h, d, r+1, out)
            return s
        return _gen
    ####################
    i = 0
    lines = op_text.split('\n')
    head, dice, res = [], [], []
    while i < len(lines):
        l = lines[i].strip(_trash)
        match = re.search(_header_regex, l.strip(_trash))
        if match:
            if debug:
                print("Matching line: %s"%l)
            die = int(match.group(1))
            outcomes = []
            descriptor = match.group(2)
            remaining = die
            j = i + 1
            while remaining > 0:
                failure = False
                if debug:
                    print("Examine next line, j = %d ; remaining = %d, printed below:\n %s " % (j, remaining, lines[j].strip(_trash)) )
                outcome_match = re.search(_line_regex, lines[j].strip(_trash))
                if outcome_match:
                    outcomes.append( (outcome_match.group(1), outcome_match.group(2) ) )
                    remaining -= 1
                j += 1
                if j - i > 3 * die:
                    #raise RuntimeError("Could not extract values for event: >> %s <<"%descriptor)
                    print("Could not extract values for event: >> %s <<"%descriptor)
                    failure = True
            if failure:
                dice.append(1)
                head.append(descriptor)
                res.append(('1', '**Could not parse.**'))
            else:
                dice.append(die)
                head.append(descriptor)
                res.append(outcomes)
            #result = roll(outcomes)
            # print("{}    \n  (d{} -> {}) {}\n\n".format(descriptor.strip(), die, result[0], result[1]))
        i += 1
    return gen(head, dice, res)

def determine_and_resolve_subroll(out):
    top = re.search('[dD](\d+)', out)
    if not top:
        return ""
    try:
        die = int(top.group(1))
        subtable = out[top.end():]
        #print("> > > Subtable identified in output:", out)
        #print("> > > Rolling a d{}, end of stuff: {}".format(die, subtable))
        slices = []
        for subroll in range(1, die):
            this_regex = "({})(.*?){}".format(subroll, subroll + 1)
            #print("> > > Attempting to match this regex:\n> {}\n> > against this\n> {}\n".format(this_regex, subtable))
            slices.append(re.search(this_regex, subtable))
            #print("> > > Examining piece %s..."%subtable)
            #if slices[-1]:
            #    print("Slice: %s"%subtable[slices[-1].start(): slices[-1].end()])
            #else:
            #    print("Regex failed.")
            if not slices[-1]:
                raise RuntimeError("Expected inline subtable, but could not parse it.")
            subtable = subtable[slices[-1].end()-len(str(subroll+1)):]
        # Did 1 through die-1.  Catch the end now
        subroll = subroll + 1
        #print("Looking for last space, item %s..."%subroll)
        slices.append(re.search("({})(.*)".format(subroll), subtable))
        suboutcome = roll(die)
        sub_re = slices[suboutcome-1]
        #print(slices)
        ret = "    \n(Inner table roll, d{} -> {}:) {}".format(die,
                                                               sub_re.group(1).strip(_trash),
                                                               sub_re.group(2).strip(_trash))
    except Exception as e:
        log("Could not resolve inline subtable; test to parse: {}".format(out))
        log("Error as follows: {}".format(e))
        print("Runtime error:", e)
        ret = "    \n>>> I'm having trouble resolving an inline subtable."
    return ret

def roll(i):
    return random.randint(1, i)

def test():
    r = sign_in()
    # already, ignore = pickle.load(open(_pickle_filename, 'rb'))
    men = r.get_mentions()
    unmen = get_unanswered_mentions(r, [])
    return r, list(men), list(unmen)

def get_post_text(post):
    '''Returns text to parse from either Comment or Submission'''
    if type(post) == praw.objects.Comment:
        return post.body
    elif type(post) == praw.objects.Submission:
        return post.selftext
    else:
        raise RuntimeError("Attempt to get post text from non-Comment / non-Submission post.")

####################

if __name__=="__main__":
    if 'y' in input("Run main?  ").lower():
        main()

