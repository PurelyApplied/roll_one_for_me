#!/usr/bin/python3
# For top-level comment scanning, you need to get submission's ID and call r.get_submission(url=None, id=ID).  Otherwise you only get the summoning comment (and perhaps the path to it)
from pprint import pprint
import string
import random
import time
import praw
import re

def doc(func):
    print(func.__doc__)

# These exist for ease of testing.
try:
    do_not_run
except:
    do_not_run = False
#do_not_run = True

##################
# Some constants #
##################
# We will strip space and punctuation
_trash = string.punctuation + string.whitespace
_header_regex = "^[dD](\d+)\s+(.*)"
_line_regex = "^(\d+)\.\s*(.*)"
_summons_regex = "/u/roll_one_for_me"
_mentions_attempts = 10
_answer_attempts = 10
_sleep_on_error = 30
_sleep_between_checks = 60 * 5

def main(debug=False):
    '''main(debug=False)
    Logs into Reddit, looks for unanswered user mentions, and generates and posts replies'''
    while True:
        try:
            r = sign_in()
            already_processed = []
            ignore_list = []
            while True:
                unanswered = get_unanswered_mentions(r, already_processed + ignore_list)
                for summons in unanswered:
                    for attempt in range(_answer_attempts):
                        try:
                            answers = get_answer(summons, r)
                            text = build_reply(answers, r, summons)
                            # TODO: Check if text is over post-length and chain replies
                            summons.reply(text)
                            already_processed.append(summons)
                        except Exception as e:
                            print("Problem answering summmons.")
                            print(e)
                            time.sleep(_sleep_on_error)
                    else:
                        print("Could not answer this summons.  Adding this comment to Ignore list")
                        ignore_list.append(summons)
                        raise RuntimeError("Error during response generation.")
                time.sleep(_sleep_between_checks)
        except Exception as e:
            print("Top level error.")
            print(e)
            print("Executing a full reset.")

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

def get_unanswered_mentions(r, already_processed):
    '''get_unanswered_mentions(r, already_processed)
    Returns a list of Reddit comments that contain your username but to which you have not yet responded.
    already_processed can be used to reduce required API calls, and is modified by this function call.'''
    for attempt in range(_mentions_attempts):
        try:
            mentions = r.get_mentions()
            unanswered = []
            for item in (i for i in mentions if i not in already_processed):
                answered_this = False
                for child in item.replies:
                    if child.author == r.user:
                        answered_this = True
                        already_processed.append(item)
                if not answered_this:
                    unanswered.append(item)
            return unanswered
        except Exception as e:
            print("Failure in get_unanswered_mentions.  Failure count: {}.".format(attempt+1) )
            print(e)
            time.sleep(_sleep_on_error)
    else:
        raise RuntimeError("Exceed error limit ({}) in get_unanswered_mentions.".format(_mentions_attempts))
        
def describe_source(post, was_OP=False):
    desc = "the original post" if was_OP else "[this]({}) comment by /u/{}".format(post.permalink, post.author)
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
            #if debug:
            #    print("Matching line: %s"%l)
            die = int(match.group(1))
            outcomes = []
            descriptor = match.group(2)
            remaining = die
            j = i + 1
            while remaining > 0:
                #if debug:
                #    print("Examine next line, j = %d ; remaining = %d " % (j, remaining) )
                outcome_match = re.search(_line_regex, lines[j].strip(_trash))
                if outcome_match:
                    outcomes.append( (outcome_match.group(1), outcome_match.group(2) ) )
                    remaining -= 1
                j += 1
                if j - i > 3 * die:
                    raise RuntimeError("Could not extract values for event: >> %s <<"%descriptor)
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
            this_regex = "({})(.*){}".format(subroll, subroll + 1)
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
        print("Runtime error:", e)
        ret = "    \n>>> I'm having trouble resolving an inline subtable."
    return ret

def roll(i):
    return random.randint(1, i)

def test():
    r = sign_in()
    men = r.get_mentions()
    unmen = get_unanswered_mentions(r, [])
    return r, list(men), list(unmen)

# Depricated / scraps

def get_post_text(post):
    '''Returns text to parse from either Comment or Submission'''
    if type(post) == praw.objects.Comment:
        return post.body
    elif type(post) == praw.objects.Submission:
        return post.selftext
    else:
        raise RuntimeError("Attempt to get post text from non-Comment / non-Submission post.")

def get_tables(text):
    pass

def generate_instance(tables):
    '''def generate_instance(tables):
    tables = ( Head_list, dice_list, results_list )
    results_list[i] is a list of dice_list[i] possible outcomes.
    These outcomes may contain an inline sublist.
    Returns ...'''
    
    pass

def generate_string(outcomes):
    pass

def generate_reply(summons, r):
    pass

####################

if __name__=="__main__" and not do_not_run:
    main()

