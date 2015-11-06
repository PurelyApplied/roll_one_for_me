import pickle

class Request:
    '''A single summons or PM.  Associate praw_ref should already be
verified to be a summons or PM request.
    '''

    def __init__(self, praw_ref):
        super(Request, self).__init__()
        self.ref = praw_ref
        self.text = praw_ref.body
        # Elements are tuple of Header, dice, text.  Will ultimately
        # generate the response text
        self.response_items = []
        self.tables_map = {}

    def __str__(self):
        return self.get_response_text()

    def __repr__(self):
        return "<Request>"

    def add_item(self, head='', roll_str='', outcome=''):
        self.response_items.append((head, roll_str, outcome))

    def add_table(self, table, key=None):
        if not key:
            key = table.header
        if key in self.tables_map:
            raise RuntimeError(
                "Table with key {!r} already present in table map.".format(key))
        self.tables_map[key] = table

    def get_response_text(self):
        return "\n\n".join(
            "    \n".join(
                item)
            for item in self.response_items)

    # Deprecated
    def get_log_str(self):
        ret_str = ''
        ret_str += "Time    :  {}\n".format(fdate())
        ret_str += "Author  :  {}\n".format(self.origin.author)
        try:
            ret_str += "Link    :  {}\n".format(self.origin.permalink)
        except:
            ret_str += "Link    :  Unavailable (PM?)\n"
            ret_str += "Type    :  {}\n".format(type(self.origin))
        try:
            ret_str += (
                "Body    : (below)\n[Begin body]\n{}\n[End body]\n".format(
                    get_post_text(self.origin)))
        except:
            ret_str += "Body    : Could not resolve message body."
        ret_str += "\n"
        try:
            f.write("Submission title : {}\n".format(
                self.origin.submission.title))
            f.write("Submission body  :"
                    " (below)\n[Begin selftext]\n{}\n[End selftext]\n".format(
                self.origin.submission.selftext))
        except:
            f.write("Submission: Could not resolve submission.")


####################
# This page: Stats for bot and bot built from components above.
class RollOneStats:
    '''Stats for /u/roll_one_for_me, to be included in message footer.'''

    def __init__(self, load_file=None):
        self.summons_answered = 0
        self.pms_replied = 0
        self.tables_rolled = 0
        self.dice_rolled = 0
        self.sentinel_posts_made = 0
        if load_file:
            self.load_data(load_file)

    def __str__(self):
        return ("Requests fulfilled: {}    \n"
                "Tables rolled: {}    \n"
                "Misc Dice Rolled: {}".format(
            self.response_count,
            self.tables_rolled_count,
            self.dice_rolled))

    def __repr__(self):
        return "<RollOneStats>"

    def __eq__(self, other):
        if not isinstance(other, RollOneStats):
            raise TypeError("RollOneStats only compares to other RollOneStats")
        # No entries are different
        return not any(getattr(self, key) != getattr(other, key)
                       for key in self.__dict__)

    def save_data(self, cache_file, tmp_file='./.tmp'):
        # Write first to a temp file to preserve the old file until
        # we're sure we have successfully written our data.  "Just in
        # case"
        with open(tmp_file, 'wb') as handle:
            pickle.dump(self, handle)
        # TODO(2016-11-02) : will this overwrite or raise an error?
        shutil.move(tmp_file, cache_file)

    def load_data(self, cache_file, raise_on_failure=True):
        if not os.path.isfile(cache_file):
            logging.error(
                "Cannot open stats file {!r}: file does not exist.".format(
                    cache_file))
            if raise_on_failure:
                raise RuntimeError("Could not open stats file")
            else:
                return
        with open(cache_file, 'wb') as handle:
            old = pickle.load(handle)
        self.__dict__.update(old.__dict__)

    def copy(self):
        copied = RollOneStats()
        copied.__dict__.update(self.__dict__)
        return copied
