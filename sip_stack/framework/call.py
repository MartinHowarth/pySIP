import re

from sip_stack.dialog import Dialog
from sip_stack.endpoint import Endpoint

from sip_stack.framework.useragent import UserAgent


class Call:
    _unique_call_id = 0
    re_from_tag = re.compile("(?:From:.*>;tag=)(.*)")

    def __init__(self, user_agent: UserAgent, destination_endpoint: Endpoint, source_endpoint: Endpoint=None,
                 call_id: str=None, subject: str=None):
        """

        :param user_agent:
        :param destination_endpoint:
        :param source_endpoint:
        :param call_id:
        :param subject:
        :return:
        """
        self.user_agent = user_agent

        # Call ID must be unique, so use and increment a global call id. If we're receiving a call then the call id is
        # specified by the remote party
        if call_id is not None:
            self.call_id = call_id
        else:
            self.call_id = self._unique_call_id
            self._unique_call_id += 1

        self.source_endpoint = (source_endpoint if source_endpoint is not None else self.user_agent.endpoint)
        self.destination_endpoint = destination_endpoint
        self.subject = subject if subject is not None else "Default"
        self.sdp = ""

        self.dialogs = {}  # From_tag: dialog.Dialog

    def new_dialog(self, from_tag: str=None):
        new_dialog = Dialog(self, from_tag)
        self.dialogs[new_dialog.from_tag] = new_dialog

    def parse_message(self, raw_message: str):
        """
        Takes a SIP messages, finds the from tag and passes the message to the relevant dialog.
        Creates a new dialog is the from tag doesn't match an existing dialog.
        :param raw_message:
        """

        from_tag = self.re_from_tag.match(raw_message).group(0)

        if from_tag in self.dialogs.keys():
            self.dialogs[from_tag].parse_message(raw_message)
        else:
            self.new_dialog(from_tag)
            self.dialogs[from_tag].parse_message(raw_message)
