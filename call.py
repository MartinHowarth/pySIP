class Call:
    _unique_call_id = 0

    def __init__(self, phone, source_endpoint, destination_endpoint, call_id=None, subject="Default"):
        """

        :param phone.Phone phone:
        :param endpoint.Endpoint source_endpoint:
        :param endpoint.Endpoint destination_endpoint:
        :param call_id:
        :param subject:
        :return:
        """
        self.phone = phone

        # Call ID must be unique, so use and increment a global call id. If we're receiving a call then the call id is
        # specified by the remote party
        if call_id is not None:
            self.call_id = call_id
        else:
            self.call_id = self._unique_call_id
            self._unique_call_id += 1

        self.source_endpoint = source_endpoint
        self.destination_endpoint = destination_endpoint
        self.subject = subject
        self.sdp = ""

        self.dialogs = {}  # From_tag: dialog.Dialog

    def receive(self, raw_message):
        """
        Takes a SIP messages, finds the from tag and passes the message to the relevant dialog.
        Creates a new dialog is the from tag doesn't match an existing dialog.
        :param str raw_message:
        """

