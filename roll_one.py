#!/usr/bin/python3

from pprint import pprint
from string import punctuation
import random
import time
import praw
import re

def doc(func):
    print(func.__doc__)

try:
    debug
except:
    debug = True

_header_regex = "^d(\d+)\s+(.*)"
_line_regex = "^(\d+)\.\s*(.*)"
_summons_regex = "/u/roll_one_for_me"

def main(debug=False):
    r = sign_in()
    already_processed = []
    while True:
        unanswered = get_unanswered_mentions(r, already_processed)
        for summons in unanswered:
            try:
                summons.reply(get_answer(summons, r))
                already_processed.append(summons)
            except:
                print("Could not answer summons.  Sleeping.")
                time.sleep(10*60)
def sign_in():
    r = praw.Reddit('Generate an outcome for random tables, under the name /u/roll_one_for_me'
                    'Written and maintained by /u/PurelyApplied')
    # login info in praw.ini
    if debug:
        print("Logging into reddit...")
    r.login()
    return r

def get_unanswered_mentions(r, already_processed):
    '''get_unanswered_mentions(r, already_processed):'''
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

def get_answer(summons, r):
    op_text = summons.submission.selftext
    gen = get_generator(op_text)
    return gen()

def get_generator(op_text):
    '''Returns generator function gen given OP text, such that gen() returns a string reply '''
    def gen(head_list, dice_list, result_list):
        assert len(head_list) == len(dice_list) == len(result_list), "Generator list length mismatch"
        def _gen():
            s = ''
            for i in range(len(head_list)):
                h = head_list[i]
                d = dice_list[i]
                r = random.randint(0, d-1)
                out = result_list[i][r][1].strip().strip(punctuation)
                out = out + determine_and_resolve_subroll(out)
                s += "{}...    \n(d{} -> {}:) {}\n\n".format(h, d, r+1, out)
            s += "-----\n^(Beep boop I'm a bot.  If it looks like I've gone off the rails and might be summoning SkyNet, let /u/PurelyApplied know.)"
            return s
        return _gen
    i = 0
    lines = op_text.split('\n')
    head, dice, res = [], [], []
    while i < len(lines):
        l = lines[i].strip()
        match = re.search(_header_regex, l.strip().strip(punctuation))
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
                outcome_match = re.search(_line_regex, lines[j].strip().strip(punctuation))
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
    top = re.search('d(\d+)', out)
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
                                                         sub_re.group(1).strip().strip(punctuation),
                                                         sub_re.group(2).strip().strip(punctuation))
    except RuntimeError as e:
        print("Runtime error:", e)
        ret = "    \n>>> I'm having trouble resolving an inline subtable."
    return ret

def roll(i):
    return random.randint(1, i)

if __name__=="__main__":
    main()
