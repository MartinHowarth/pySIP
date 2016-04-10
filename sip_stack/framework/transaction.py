from sip_stack.framework import message
from sip_stack.framework.dialog import Dialog


class Transaction:
    _branch_counter = 0

    def __init__(self, dialog: Dialog, branch: str=None):
        """

        :param dialog:
        :param branch:
        :return:
        """
        self.dialog = dialog

        if branch is None:
            self.branch = "z9hG4bK" + "_" + str(self._branch_counter)
            self._branch_counter += 1
        else:
            self.branch = branch

        self.messages = []

    def parse_message(self, raw_message: str):
        """
        Takes a SIP message and creates a message.Message object to represent it.
        :param raw_message:
        """
        self.messages.append(message.message_factory(self, raw_message))
