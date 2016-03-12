class Message:
    _request_line_initial = "%(type)s sip:%(destination_number)s@%(domain)s SIP/2.0"
    _request_line_response = "SIP/2.0 %(response_number) %(type)s"
    _via_line = "Via: SIP/2.0/%(transport)s %(local_ip)s:%(local_port)s;branch=%(branch)s"
    _from_line = "From: %(user_agent)s <sip:%(source_number)s@%(local_ip)s:%(local_port)s>;tag=%(tag)s"
    _to_line = "To: %(destination_number)s <sip:%(destination_number)s@%(domain)s:%(remote_port)s>"
    _call_id_line = "Call-ID: %(call_id)s"
    _cseq_line = "CSeq: 1 %(type)s"
    _contact_line = "Contact: sip:%(source_number)s@%(local_ip)s:%(local_port)s"
    _max_forwards_line = "Max-Forwards: %(max_forwards)s"
    _subject_line = "Subject: %(subject)s"
    _content_type_line = "Content-Type: %(content_type)s"
    _content_length_line = "Content-Length: %(content_length)s"
    _sdp = "\n%(sdp)s"

    def __init__(self, message_type, response_number=None):
        self._message = None

        self.type = message_type
        self.response_number = response_number
        self.local_ip = ""
        self.local_port = 0
        self.remote_port = 0
        self.branch = ""
        self.destination_number = ""
        self.source_number = ""
        self.domain = ""
        self.call_id = ""
        self.user_agent = ""
        self.tag = "0"
        self.max_forwards = 70
        self.subject = "Default"
        self.content_type = "application/sdp"
        self.content_length = 0
        self.transport = "UDP"
        self.sdp = ""

        """
        INVITE sip:{{destination_number}}@{{domain}} SIP/2.0
        Via: SIP/2.0/[transport] [local_ip]:[local_port];branch=[branch]
        From: ua[call_number] <sip:{{source_number}}@[local_ip]:[local_port]>;tag=[call_number]
        To: {{destination_number}} <sip:{{destination_number}}@{{domain}}:[remote_port]>
        Call-ID: [call_id]
        CSeq: 1 INVITE
        Contact: sip:{{source_number}}@[local_ip]:[local_port]
        Max-Forwards: 70
        Subject: Performance Test
        Content-Type: application/sdp
        Content-Length: [len]

        {{sdp}}
        """
        """
        SIP/2.0 200 OK
        [last_Via:]
        [last_From:]
        [last_To:];tag=[call_number]
        [last_Call-ID:]
        [last_CSeq:]
        Contact: <sip:[local_ip]:[local_port];transport=[transport]>
        Content-Type: application/sdp
        Content-Length: [len]

        {{sdp}}
        """

    @property
    def message(self):
        self.construct()
        return self._message

    @message.setter
    def message(self, value):
        self._message = value
        self.deconstruct()

    def construct(self):
        """
        Construct the SIP message from parameters.
        """

        self._construct_sdp()
        self._calculate_content_length()

        # First line of the SIP message depends on whether this is a response or not. (Response e.g. 200 OK)
        if self.response_number is not None:
            _request_line = self._request_line_response
        else:
            _request_line = self._request_line_initial

        self._message = ""
        for line in (_request_line,
                     self._via_line,
                     self._from_line,
                     self._to_line,
                     self._call_id_line,
                     self._cseq_line,
                     self._contact_line,
                     self._max_forwards_line,
                     self._subject_line,
                     self._content_type_line,
                     self._content_length_line,
                     self._sdp):
            self._message += line % self.__dict__ + "\n"

        """
        INVITE sip:{{destination_number}}@{{domain}} SIP/2.0
        Via: SIP/2.0/[transport] [local_ip]:[local_port];branch=[branch]
        From: ua[call_number] <sip:{{source_number}}@[local_ip]:[local_port]>;tag=[call_number]
        To: {{destination_number}} <sip:{{destination_number}}@{{domain}}:[remote_port]>
        Call-ID: [call_id]
        CSeq: 1 INVITE
        Contact: sip:{{source_number}}@[local_ip]:[local_port]
        Max-Forwards: 70
        Subject: Performance Test
        Content-Type: application/sdp
        Content-Length: [len]

        {{sdp}}
        """

    def _construct_sdp(self):
        self.sdp = ""

    def _calculate_content_length(self):
        self.content_length = len(self.sdp)

    def deconstruct(self):
        """
        Deconstruct the current SIP message into parameters of this class
        """


class RawMessage(Message):
    """
    A Completely user defined message.
    """
    def __init__(self, raw_message, message_type=None):
        super().__init__(message_type)
        self.message = raw_message

    def construct(self):
        """
        Raw messages may not map onto the defined parameters of a Message so raw messages override the deconstructor
        """

    def deconstruct(self):
        """
        Raw messages may not map onto the defined parameters of a Message so raw messages override the constructor
        """


class Invite(Message):
    def __init__(self):
        super(Invite, self).__init__("INVITE")

        """
        INVITE sip:{{destination_number}}@{{domain}} SIP/2.0
        Via: SIP/2.0/[transport] [local_ip]:[local_port];branch=[branch]
        From: ua[call_number] <sip:{{source_number}}@[local_ip]:[local_port]>;tag=[call_number]
        To: {{destination_number}} <sip:{{destination_number}}@{{domain}}:[remote_port]>
        Call-ID: [call_id]
        CSeq: 1 INVITE
        Contact: sip:{{source_number}}@[local_ip]:[local_port]
        Max-Forwards: 70
        Subject: Performance Test
        Content-Type: application/sdp
        Content-Length: [len]

        {{sdp}}
        """


class Ok(Message):
    def __init__(self):
        super(Ok, self).__init__("OK", response_number=200)

        """
        SIP/2.0 200 OK
        [last_Via:]
        [last_From:]
        [last_To:];tag=[call_number]
        [last_Call-ID:]
        [last_CSeq:]
        Contact: <sip:[local_ip]:[local_port];transport=[transport]>
        Content-Type: application/sdp
        Content-Length: [len]

        {{sdp}}
        """
