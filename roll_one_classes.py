'''Class definitions for the roll_one_for_me bot

A Request fetches the submission and top-level comments of the appropraite thread.
Each of these items become a TableSource.
A TableSource is parsed for Tables.
A Table contains many TableItems.
When a Table is rolled, the appropraite TableItems are identified.
These are then built into TableRoll objects for reporting.
'''

from roll_one_util import *

import random, praw, re, pickle, string, time
from pprint import pprint  #for debugging / live testing

class Request:
    def __init__(self, praw_ref, r):
        self.origin = praw_ref
        self.reddit = r
        self.tables_sources = []
        self.outcome = None

        self._parse()

    def __repr__(self):
        return "<Request from /u/{} in thread \"{}\">".format(self.origin.author, self.origin.submission.title)

    def _parse(self):
        '''Fetches text of submission and top-level comments from thread
        containing this Request.  Builds a TableSource for each, and
        attempts to parse each for tables.

        '''
        T = TableSource(self.origin.submission, "this thread's original post")
        if T.has_tables():
            self.tables_sources.append(T)
        top_level_comments = self.reddit.get_submission(None, self.origin.submission.id).comments
        for item in top_level_comments:
            T = TableSource(item, "[this]({}) comment by {}".format(item.permalink, item.author) )
            if T.has_tables():
                T._parse()
                self.tables_sources.append(T)

    def roll(self):
        instance = [TS.roll() for TS in self.tables_sources]
        instance = [x for x in instance if x]
        return "\n\n-----\n\n".join(instance)

    def reply(self, reply_text):
        self.origin.reply(reply_text)

    def is_summons(self):
        return re.search(_summons_regex, get_post_text(self.origin).lower())

    def log(self, log_dir):
        filename = "{}/{}-{}.log".format(log_dir, self.origin.author, self.origin.fullname)
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
        instance = [x for x in instance if x]
        if instance:
            ret = "From {}...\n\n".format(self.desc)
            for item in instance:
                ret += item.unpack()
            return ret
        return None

    def has_tables(self):
        return ( 0 < len(self.tables) )

    def _parse(self):
        indices = []
        last_index = 0
        text = get_post_text(self.source)
        lines = text.split("\n")
        for line_num in range(len(lines)):
            l = lines[line_num]
            if re.search(_header_regex, l.strip(_trash)):
                indices.append(line_num)
        # TODO: if no headers found?
        if len(indices) == 0:
            return None

        table_text = []
        for i in range(len(indices) -1):
            table_text.append("\n".join(lines[ indices[i]:indices[i+1] ]))
        table_text.append("\n".join(lines[ indices[-1]: ]))

        self.tables = [ Table(t) for t in table_text ]

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
        last_index = 0
        text = self.text
        lines = text.split("\n")
        for line_num in range(len(lines)):
            l = lines[line_num]
            if re.search(_header_regex, l.strip(_trash)):
                indices.append(line_num)
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
        self.is_inline = False

        self._parse()

    def __repr__(self):
        return "<Table with header: {}>".format(self.text.split('\n')[0])

    def _parse(self):
        lines = self.text.split('\n')
        head = lines.pop(0)
        head_match = re.search(_header_regex, head.strip(_trash))
        if head_match:
            self.die = int(head_match.group(2))
            self.header = head_match.group(3)
        self.outcomes = [ TableItem(l) for l in lines if re.search(_line_regex, l.strip(_trash)) ]

    def roll(self):
        try:
            weights = [ i.weight for i in self.outcomes]
            total_weight = sum(weights)
            if debug:
                print("Weights ; Outcome")
                pprint(list(zip(self.weights, self.outcomes)))
            assert self.die == total_weight, "Table roll error: parsed die did not match sum of item wieghts."
            stops = [ sum(weights[:i+1]) for i in range(len(weights))]
            c = random.randint(1, self.die)
            scan = c
            ind = -1
            while scan > 0:
                ind += 1
                scan -= weights[ind]

            R = TableRoll(d=self.die,
                          rolled=c,
                          head=self.header,
                          out=self.outcomes[ind])
            if len(self.outcomes) != self.die:
                R.error("Expected {} items found {}".format(self.die, len(self.outcomes)))
            return R
        # TODO: Handle errors more gracefully.
        except Exception as e:
            logger("Exception in Table roll ({}): {}".format(self, e), _log_filename, debug)
            return None

class TableItem:
    '''This class allows simple handling of in-line subtables'''
    def __init__(self, text, w=0):
        self.text = text
        self.inline_table = None
        self.outcome = ""
        self.weight = 0

        self._parse()

        # If parsing fails, particularly in inline-tables, we may want
        # to explicitly set weights
        if w:
            self.weight = w

    def __repr__(self):
        return "<TableItem: {}{}>".format(self.outcome, "; has inline table" if self.inline_table else "")

    def _parse(self):
        main_regex = re.search(_line_regex, self.text.strip(_trash))
        if not main_regex:
            return
        # Grab outcome
        self.outcome = main_regex.group(3).strip(_trash)
        # Get weight / ranges
        if not main_regex.group(2):
            self.weight = 1
        else:
            try:
                start = int(main_regex.group(1).strip(_trash))
                stop = int(main_regex.group(2).strip(_trash))
                self.weight = stop - start + 1
            except:
                self.weight = 1
        # Identify if there is a subtable
        if re.search("[dD]\d+", self.outcome):
            die_regex = re.search("[dD]\d+", self.outcome)
            try:
                self.inline_table = InlineTable(self.outcome[die_regex.start():])
            except RuntimeError as e:
                logger("Error in inline_table parsing ; table item full text:", _log_filename, debug)
                logger(self.text, _log_filename, debug)
                logger(e, _log_filename, debug)
                self.outcome = self.outcome[:die_regex.start()].strip(_trash)
        # this might be redundant
        self.outcome = self.outcome.strip(_trash)


    def get(self):
        if self.inline_table:
            return self.outcome + self.inline_table.roll()
        else:
            return self.outcome

class InlineTable(Table):
    '''A Table object whose text is parsed in one line, instead of expecting line breaks'''
    def __init__(self, text):
        super().__init__(text)
        self.is_inline = True

    def __repr__(self):
        return "<d{} Inline table>".format(self.die)

    def _parse(self):
        top = re.search("[dD](\d+)(.*)", self.text)
        if not top:
            return

        self.die = int(top.group(1))
        tail = top.group(2)
        sub_outs = []
        while tail:
            in_match = re.search(_line_regex, tail.strip(_trash))
            if not in_match:
                raise RuntimeError("Could not complete parsing InlineTable; in_match did not catch.")
            this_out = in_match.group(3)
            next_match = re.search(_line_regex[1:], this_out)
            if next_match:
                tail = this_out[next_match.start():]
                this_out = this_out[:next_match.start()]
            else:
                tail = ""

            TI_text = in_match.group(1) + (in_match.group(2) if in_match.group(2) else "") + this_out
            try:
                self.outcomes.append(TableItem(TI_text))
            except Exception as e:
                logger("Error building TableItem in inline table; item skipped.", _log_filename, debug)

class TableRoll:
    def __init__(self, d, rolled, head, out, err=None):
        self.d = d
        self.rolled = rolled
        self.head = head
        self.out = out
        self.sub = out.inline_table
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
            ret += "Subtable: {}".format(self.sub.roll().unpack())
        ret += "\n\n"
        return ret
