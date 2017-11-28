import logging
import random
import re
import string

from praw.exceptions import PRAWException
from praw.models import Comment, Submission, Message

from classes.reddit.endpoint import Reddit as FutureReddit

_header_regex = "^(\d+)?[dD](\d+)(.*)"
_line_regex = "^(\d+)(\s*-+\s*\d+)?(.*)"
_summons_regex = "u/roll_one_for_me"

_trash = string.punctuation + string.whitespace


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
        return 0 < len(self.tables)

    def _parse(self):
        indices = []
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
        for i in range(len(indices) - 1):
            table_text.append("\n".join(lines[indices[i]:indices[i + 1]]))
        table_text.append("\n".join(lines[indices[-1]:]))

        self.tables = [Table(t) for t in table_text]


class Table:
    """Container for a single set of TableItem objects
    A single post will likely contain many Table objects"""

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
        self.outcomes = [TableItem(l) for l in lines if re.search(_line_regex, l.strip(_trash))]

    def roll(self):
        try:
            weights = [i.weight for i in self.outcomes]
            total_weight = sum(weights)
            if self.die != total_weight:
                self.header = "[Table roll error: parsed die did not match sum of item weights.]  \n" + self.header
            # stops = [ sum(weights[:i+1]) for i in range(len(weights))]
            c = random.randint(1, self.die)
            scan = c
            ind = -1
            while scan > 0:
                ind += 1
                scan -= weights[ind]

            table_roll = TableRoll(d=self.die,
                                   rolled=c,
                                   head=self.header,
                                   out=self.outcomes[ind])
            if len(self.outcomes) != self.die:
                table_roll.error("Expected {} items found {}".format(self.die, len(self.outcomes)))
            return table_roll
        except Exception as e:
            legacy_log("Exception in Table roll ({}): {}".format(self, e))
            return None


# noinspection PyBroadException
class TableItem:
    """This class allows simple handling of in-line subtables"""

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
        # Identify if there is a sub-table
        if re.search("[dD]\d+", self.outcome):
            die_regex = re.search("[dD]\d+", self.outcome)
            try:
                self.inline_table = InlineTable(self.outcome[die_regex.start():])
            except RuntimeError as e:
                legacy_log("Error in inline_table parsing ; table item full text:")
                legacy_log(self.text)
                legacy_log(e)
                self.outcome = self.outcome[:die_regex.start()].strip(_trash)
        # this might be redundant
        self.outcome = self.outcome.strip(_trash)

    def get(self):
        if self.inline_table:
            return self.outcome + self.inline_table.roll()
        else:
            return self.outcome


# noinspection PyBroadException
class InlineTable(Table):
    """A Table object whose text is parsed in one line, instead of expecting line breaks"""

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
        # sub_outs = []
        while tail:
            in_match = re.search(_line_regex, tail.strip(_trash))
            if not in_match:
                legacy_log("Could not complete parsing InlineTable; in_match did not catch.")
                legacy_log("Returning blank roll area.")
                self.outcomes = [TableItem("1-{}. N/A".format(self.die))]
                return
            this_out = in_match.group(3)
            next_match = re.search(_line_regex[1:], this_out)
            if next_match:
                tail = this_out[next_match.start():]
                this_out = this_out[:next_match.start()]
            else:
                tail = ""

            t_i_text = in_match.group(1) + (in_match.group(2) if in_match.group(2) else "") + this_out
            try:
                self.outcomes.append(TableItem(t_i_text))
            except Exception:
                logging.exception("Error building TableItem in inline table; item skipped.")


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
        ret = "{}...    \n".format(self.head.strip(_trash))
        ret += "(d{} -> {}) {}.    \n".format(self.d, self.rolled, self.out.outcome)
        if self.sub:
            ret += "Subtable: {}".format(self.sub.roll().unpack())
        ret += "\n\n"
        return ret


# noinspection PyBroadException
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
        if type(self.origin) == Comment:
            via = "mention in {}".format(self.origin.submission.title)
        elif type(self.origin) == Message:
            via = "private message"
        else:
            via = "a mystery!"
        return "/u/{} via {}".format(self.origin.author, via)

    def _parse(self):
        """Fetches text of submission and top-level comments from thread
        containing this Request.  Builds a TableSource for each, and
        attempts to parse each for tables.

        """
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
        t = TableSource(source, desc)
        if t.has_tables():
            self.tables_sources.append(t)

    def get_link_sources(self):
        links = re.findall("\[.*?\]\s*\(.*?\)", self.origin.body)
        # print("Link set:", file=sys.stderr)
        # print("\n".join([str(l) for l in links]), file=sys.stderr)
        for item in links:
            desc, href = re.search("\[(.*?)\]\s*\((.*?)\)", item).groups()
            href = href.strip()
            if "reddit.com" in href.lower():
                legacy_log("Fetching href: {}".format(href.lower()))
                if "m.reddit" in href.lower():
                    legacy_log("Removing mobile 'm.'")
                    href = href.lower().replace("m.reddit", "reddit", 1)
                if ".json" in href.lower():
                    legacy_log("Pruning .json and anything beyond.")
                    href = href[:href.find('.json')]
                if 'www' not in href.lower():
                    legacy_log("Injecting 'www.' to href")
                    href = href[:href.find("reddit.com")] + 'www.' + href[href.find("reddit.com"):]
                href = href.rstrip("/")
                legacy_log("Processing href: {}".format(href))

                self._maybe_add_source(FutureReddit.try_to_follow_link(href), desc)

    def get_default_sources(self):
        """Default sources are OP and top-level comments"""
        try:
            # Add OP
            self._maybe_add_source(self.origin.submission, "this thread's original post")
            # Add Top-level comments
            top_level_comments = FutureReddit.r.submission(self.origin.submission).comments
            for item in top_level_comments:
                self._maybe_add_source(item, "[this]({}) comment by {}".format(item.permalink, item.author))
        except:
            legacy_log("Could not add default sources.  (PM without links?)")

    def roll(self):
        instance = [TS.roll() for TS in self.tables_sources]
        instance = [x for x in instance if x]
        return "\n\n-----\n\n".join(instance)

    def reply(self, reply_text):
        self.origin.reply(reply_text)

    def is_summons(self):
        return re.search(_summons_regex, get_post_text(self.origin).lower())

    def is_private_message(self):
        return isinstance(self.origin, Message)

    # This function is unused, but may be useful in future logging
    def describe_source(self):
        return "From [this]({}) post by user {}...".format(self.origin.permalink, self.origin.author)


# Testing only
# noinspection PyMissingConstructor
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
            if re.search(_header_regex, l.strip(_trash)):
                indices.append(line_num)
        if len(indices) == 0:
            return None
        table_text = []
        for i in range(len(indices) - 1):
            table_text.append("\n".join(lines[indices[i]:indices[i + 1]]))
        table_text.append("\n".join(lines[indices[-1]:]))
        self.tables = [Table(t) for t in table_text]


def get_post_text(post):
    """Returns text to parse from either Comment or Submission"""
    if type(post) == Comment:
        try:
            logging.debug("Try the body, it's fresh")
            return post.body
        except PRAWException:
            logging.exception("Hopefully, I'm catching a \"Had no comment\" exception.  Convoluted to-sub thing!")
            convoluted_id = FutureReddit.r.submission(id=post.id).id_from_url((post.id))
            submission = FutureReddit.r.submission(convoluted_id)
            return submission.selftext

    elif type(post) == Submission:
        return post.selftext
    else:
        legacy_log("Attempt to get post text from"
                   " non-Comment / non-Submission post; returning empty string")
        return ""


def legacy_log(l):
    logging.debug(l)


