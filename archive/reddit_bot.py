import time
import logging
import praw


####################
## This page: Basic Reddit access and mail fetching
class RedditBot:
    '''Base for Reddit bot components.  Handles login, provides reddit
handle at self.r.
    '''
    def __init__(self, sign_in=True, **kwargs):
        self.r = None
        super(RedditBot, self).__init__(**kwargs)
        if sign_in:
            self.sign_in(**kwargs)

    def sign_in(self, sign_in_attempts=5, sleep_on_failure=30):
        '''Signs into Reddit, attempting $sign_in_attempts attempts before
returning an error.
        '''
        for i in range(sign_in_attempts):
            try:
                logging.info("Attempting to sign in...")
                r = self._attempt_sign_in()
                logging.info("Signed in.")
                return r
            except Exception as e:
                #requests.exceptions.ConnectionError
                #praw.objects.ClientException
                print("Got type", type(e))
                print(e)
                logging.info("Sign in failed.  Sleeping...")
                time.sleep(sleep_on_failure)
        logging.critical("Could not sign in after {} attempts.  Crashing out.")
        raise RuntimeError("Could not sign in.")

    def _attempt_sign_in(self):
        '''Attempt to sign into Reddit.  This function assumes a properly
OAuth-configured praw.ini file.
        '''
        r = praw.Reddit(
            user_agent=(
                'Generate an outcome for random tables, under the name'
                ' /u/roll_one_for_me.'
                ' Written and maintained by /u/PurelyApplied'),
            site_name="roll_one")
        r.refresh_access_information()
        self.r = r



class MailHandling(RedditBot):
    '''Mail and mention handling wrapper.'''
    def __init__(self):
        super(MailHandling, self).__init__()

    def __repr__(self):
        return "<MailHandler>"

    def fetch_new_mail(self, unset=False, **kwargs) -> list:
        '''Fetches any mail currently set as unread.  Does not unset
notification by default.  kwargs passed to praw's get_unread'''
        kwargs.update({'unset_has_mail' : unset})
        return list(self.r.get_unread(**kwargs))

    def fetch_inbox(self, **kwargs) -> list:
        '''Fetches all mail in inbox.  kwargs passed to praw's get-inbox.
        Does not unset notification, overwriting kwargs if necessary.
        (Use fetch_new_mail instead.)

        '''
        # Fetches all inbox messages and mentions
        kwargs['unset_has_mail'] = False
        return list(self.r.get_inbox(**kwargs))

    def fetch_mentions(self, **kwargs) -> list:
        '''Fetches user mentions. kwargs passed to praw's get_mentions.
        Does not unset notification, overwriting kwargs if necessary.
        (Use fetch_new_mail instead.)

        '''
        kwargs['unset_has_mail'] = False
        return list(self.r.get_mentions(**kwargs))
