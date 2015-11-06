from collections import deque
from enum import Enum

import praw

from archive.reddit_bot import RedditBot

####################
## This page: Table and Request processing

class TableProcessing(RedditBot):
    def __init__(self, **kwargs):
        super(TableProcessing, self).__init__(**kwargs)

    def get_table_sources(self, request,
                          include_provided = True,
                          get_OP = True,
                          get_top_level = True,
                          get_links = True):
        body = root_ref.body
        table_sources = []
        logging.debug("Generating table sources...")
        if include_provided:
            logging.debug("Converting mail itself...")
            table_sources += [TableSource(body)]
        if get_OP and isinstance(root_ref, praw.objects.Comment):
            logging.debug("Fetching OP...")
            op_ref = self.r.get_submission(
                submission_id=root_ref.submission.id)
            logging.debug("Converting OP to TableSource...")
            table_sources += [TableSource(op_ref.selftext)]
        if get_top_level and isinstance(root_ref, praw.objects.Comment):
            logging.debug("Converting top-level comments to TableSource...")
            table_sources += [TableSource(c.body) for c in op_ref.comments]
        if get_links and isinstance(root_ref, praw.objects.Comment):
            logging.debug("Searching for links...")
            link_texts = re.findall(r"\[.*?\]\(.*?\)", body)
            link_urls = [re.search(r"\[.*.\]\((.*)\)", l).group(1)
                         for l in link_texts]
            logging.debug("Fetching submissions from urls...")
            link_refs = [self.r.get_submission(url) for url in link_urls]
            logging.debug("Converting found links to TableSource...")
            table_sources += [TableSource(l.selftext
                                          if hasattr(l, 'selftext')
                                          else (l.body
                                                if hasattr(l, 'body')
                                                else '')) for l in link_refs]
        logging.debug("Removing nil TableSources")
        return [t for t in table_sources if t]

    

COMMANDS = Enum('request',
                [
                    # These are general categoricals; requires no args
                    'roll_requesting',
                    'roll_op',
                    'roll_top_level',
                    'roll_link',
                    'provide_organizational',
                    # These will require specific arguments
                    'roll_dice', # Takes die notation as arg
                    'roll_table_with_tag', # Takes tag as arg
                ])



class RequestProcessing(TableProcessing):
    def __init__(self, **kwargs):
        super(RequestProcessing, self).__init__(**kwargs)
        # Queue elements will be of the above enum, possibly paired
        # with args:  (cmd, args)
        self.queue = deque()

    def _default_queue(self):
        '''Produces the default repsonse queue: request, OP, top level'''
        # TODO: add self?
        self.queue = deque([COMMANDS.roll_top_level,
                            COMMANDS.roll_op,
                            COMMANDS.roll_requesting])

    def _build_queue_from_tags(self, explicit_command_tags, link_tags):
        pass

    def build_process_queue(self, request):
        explicit_command_tags = re.findall(r"\[\[.*?\]\]", request.text)
        link_tags = re.findall(r"\[[^\[]*?\]\s*\(.*?\)", request.text)
        if not explicit_command_tags and not link_tags:
            self._default_queue()
        else:
            self._build_queue_from_tags(explicit_command_tags, link_tags)

    def process_request(self, request):
        self.build_process_queue(self, request)
        while self.process_queue:
            # process one command
            # Append an item to request.response_items
            pass

    def respond_to_request(self, mention_ref):
        # Todo: there's a lot of potential optimization to be done
        # here.  If someone just calls '[[roll DICE]]' for instance, I
        # wouldn't need all the references.
        logging.debug("Searching for commands...")
        commands = re.findall(r"\[\[(.+?)\]\]", mention_ref.body)
        logging.debug("Commands found: {}".format(commands))
        logging.info("Generating response to user-mention")
        sources = self.get_table_sources(mention_ref)
        logging.info("Table sources generated.  Generating response.")
        # respond, marks as read.
        # Possible sources: summoning comment, OP, top-level comments
        # to OP, any links in summoning text
        logging.info("Generating reply...")
        # mention_ref.mark_as_read()


        
