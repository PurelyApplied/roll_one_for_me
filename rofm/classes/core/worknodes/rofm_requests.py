from abc import ABC
from dataclasses import dataclass, field
from typing import Dict, Any, Union

# noinspection PyMethodParameters
import praw.models
from anytree import RenderTree

from rofm.classes.core.worknodes import rofm_core, rofm_parsers


@dataclass
class Request(rofm_core.Worknode, ABC):
    args: Union[praw.models.Message, praw.models.Comment]
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: rofm_core.WorkloadType = rofm_core.WorkloadType.request_type_private_message
    name: str = "Request via PM"

    def __str__(self):
        return "\n\n\n".join((str(work) for work in self.additional_work if str(work))) + self.beep_boop()

    def beep_boop(self):
        return ("*Beep boop, I'm a bot.*\n\n"
                "*I am maintained by /u/PurelyApplied,"
                " for whom these username mentions are a huge morale boost.*\n\n"
                "*You can find my source code and more details about me"
                " on [GitHub](https://github.com/PurelyApplied/roll_one_for_me).*\n\n"
                "*The following is the work I did for you!"
                "  I'm posting it for now for easier debugging and a little robot humble-bragging.*\n\n"
                f"{self._get_indented_render_tree()}"
                )

    def _get_indented_render_tree(self):
        return "\n".join(f"    {pre}{node}" for pre, _, node in (RenderTree(self)))


@dataclass
class PrivateMessage(Request):
    args: praw.models.Message
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: rofm_core.WorkloadType = rofm_core.WorkloadType.request_type_private_message
    name: str = "Request via PM"

    def __str__(self):
        return super(PrivateMessage, self).__str__()

    def __repr__(self):
        return super(PrivateMessage, self).__repr__()

    def _my_work_resolver(self):
        self.additional_work = [
            rofm_parsers.RedditDomainUrls(self.args),
            rofm_parsers.Message(self.args),
            rofm_parsers.SpecialRequest(self.args)
        ]


@dataclass
class UsernameMention(rofm_core.Worknode):
    args: praw.models.Comment
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: rofm_core.WorkloadType = rofm_core.WorkloadType.request_type_username_mention
    name: str = "Request via username mention"

    def __str__(self):
        return super(UsernameMention, self).__str__()

    def __repr__(self):
        return super(UsernameMention, self).__repr__()

    def _my_work_resolver(self):
        # Until it is decided otherwise, a mention gets three actions:
        # (1) Look at the comment itself for a table
        # (2) Look for reddit-domain links to parse.
        # (2.1) Distinguish from links to submission (which also get top-level comments) and
        # (2.2) Comments, which maybe get the full treatment?
        # (3) Look at the OP
        # (4) Look at the top-level comments.
        mention = self.args
        op = mention.submission
        top_level_comments = list(op.comments)
        if mention in top_level_comments:
            top_level_comments.remove(mention)

        self.additional_work = [
            rofm_parsers.Comment(mention),
            rofm_parsers.RedditDomainUrls(mention),
            rofm_parsers.Submission(op),
            rofm_parsers.TopLevelComments(top_level_comments)
        ]
