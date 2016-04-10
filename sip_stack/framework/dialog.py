import re

from sip_stack.framework import transaction


class Dialog:
    _unique_tag = 0
    re_branch = re.compile("(?:Via:.*;branch=)(.*)")

    def __init__(self, call, from_tag=None):
        """

        :param call.Call call:
        :param from_tag:
        :return:
        """
        self.call = call

        # From tag must be unique, so simply use and increment a global tag id.
        # If we are the callee, then the remote party specifies the from tag and we specify the to tag
        if from_tag is not None:
            self.from_tag = from_tag
            self.to_tag = self._unique_tag
            self._unique_tag += 1
        else:
            self.from_tag = str(self._unique_tag) + \
                            "@%s:%s" % (self.call.source_endpoint.ip, self.call.source_endpoint.port)
            self._unique_tag += 1
            # Cannot determine to tag until the other side has responded
            self.to_tag = None

        self.transactions = {}  # branch: transaction.Transaction

    def new_transaction(self, branch=None):
        new_transaction = transaction.Transaction(self, branch)
        self.transactions[new_transaction.branch] = new_transaction

    def parse_message(self, raw_message):
        """
        Takes a SIP messages, finds the branch and passes the message to the relevant transaction.
        Creates a new transaction if the branch doesn't match an existing transaction.
        :param str raw_message:
        """

        branch = self.re_branch.match(raw_message).group(0)
        self.new_transaction(branch)
        self.transactions[branch].parse_message(raw_message)
