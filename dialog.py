class Dialog:
    _unique_tag = 0

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
            self.from_tag = self._unique_tag
            self._unique_tag += 1
            # Cannot determine to tag until the other side has responded
            self.to_tag = None

        self.transactions = {}  # branch: transaction.Transaction

    def receive(self, raw_message):
        """
        Takes a SIP messages, finds the branch and passes the message to the relevant transaction.
        Creates a new transaction if the branch doesn't match an existing transaction.
        :param str raw_message:
        """

