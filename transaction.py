import message


class Transaction:
    _branch_counter = 0

    def __init__(self, dialog, branch=None):
        """

        :param dialog.Dialog dialog:
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

    def parse_message(self, raw_message):
        """
        Takes a SIP message and creates a message.Message object to represent it.
        :param str raw_message:
        """
        self.messages.append(message.message_factory(self, raw_message))
