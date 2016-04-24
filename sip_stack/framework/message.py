import re

from sip_stack.framework.transaction import Transaction


class SipMessage:
    re_message_type = re.compile("([A-Z]{1,10})(?![\/:A-Za-z])")
    re_content_type = re.compile("(?:Content-Type:)[ ]?(.*)")
    re_content_length = re.compile("(?:Content-Length:)[ ]?(.*)")
    re_subject = re.compile("(?:Subject:)[ ]?(.*)")
    re_max_forwards = re.compile("(?:Max-Forwards:)[ ]?(.*)")
    re_expires = re.compile("(?:Expires:)[ ]?(.*)")
    re_body = re.compile("(?:\n\n)(.*)")

    _request_line_initial = "%(type)s sip:%(destination_number)s@%(domain)s SIP/2.0"
    _request_line_response = "SIP/2.0 %(response_number)s %(type)s"
    _via_line = "Via: SIP/2.0/%(transport)s %(via_ip)s:%(via_port)s;branch=%(branch)s"
    _from_line = "From: %(user_agent)s <sip:%(source_number)s@%(source_ip)s:%(source_port)s>"
    _from_tag = ";tag=%(from_tag)s"
    _to_line = "To: %(destination_number)s <sip:%(destination_number)s@%(domain)s:%(destination_port)s>"
    _to_tag = ";tag=%(to_tag)s"
    _call_id_line = "Call-ID: %(call_id)s"
    _cseq_line = "CSeq: 1 %(type)s"
    _contact_line = "Contact: sip:%(source_number)s@%(source_ip)s:%(source_port)s"
    _max_forwards_line = "Max-Forwards: %(max_forwards)s"
    _subject_line = "Subject: %(subject)s"
    _content_type_line = "Content-Type: %(content_type)s"
    _content_length_line = "Content-Length: %(content_length)s"
    _body = "\n%(body)s"

    def __init__(self, transaction: Transaction, message_type: str, body: str=None, response_number: int=None):
        """

        :param transaction:
        :param message_type:
        :param response_number:
        :return:
        """
        self._message = None
        self.additional_template_lines = []

        self.source_ip = transaction.dialog.call.source_endpoint.ip
        self.source_port = transaction.dialog.call.source_endpoint.port
        self.destination_port = transaction.dialog.call.destination_endpoint.port
        self.via_ip = transaction.dialog.call.destination_endpoint.via_ip
        self.via_port = transaction.dialog.call.destination_endpoint.via_port
        self.transport = transaction.dialog.call.destination_endpoint.transport
        self.source_number = transaction.dialog.call.source_endpoint.number
        self.domain = transaction.dialog.call.destination_endpoint.domain
        self.user_agent = transaction.dialog.call.user_agent.endpoint.user_agent
        self.destination_number = transaction.dialog.call.destination_endpoint.number
        self.call_id = transaction.dialog.call.call_id
        self.subject = transaction.dialog.call.subject
        self.sdp = transaction.dialog.call.sdp
        self.to_tag = transaction.dialog.to_tag
        self.from_tag = transaction.dialog.from_tag
        self.branch = transaction.branch
        self.max_forwards = 70
        self.content_type = "application/sdp"
        self.content_length = 0
        self.type = message_type
        self.response_number = response_number

        self.body = body

        """
        INVITE sip:{{destination_number}}@{{domain}} SIP/2.0
        Via: SIP/2.0/[transport] [source_ip]:[source_port];branch=[branch]
        From: ua[call_number] <sip:{{source_number}}@[source_ip]:[source_port]>;tag=[call_number]
        To: {{destination_number}} <sip:{{destination_number}}@{{domain}}:[destination_port]>
        Call-ID: [call_id]
        CSeq: 1 INVITE
        Contact: sip:{{source_number}}@[source_ip]:[source_port]
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
        Contact: <sip:[source_ip]:[source_port];transport=[transport]>
        Content-Type: application/sdp
        Content-Length: [len]

        {{sdp}}
        """

    @property
    def message(self):
        self.construct_template()
        self._message = self._message % self.__dict__
        return self._message

    @message.setter
    def message(self, value):
        self._message = value
        self.deconstruct()

    def construct_template(self):
        """
        Construct the SIP message template. No parameters are filled in, but have placeholders such as %(param)s
        """

        self._calculate_content_length()

        # First line of the SIP message depends on whether this is a response or not. (Response e.g. 200 OK)
        if self.response_number is not None:
            _request_line = self._request_line_response
        else:
            _request_line = self._request_line_initial

        # Construct the message with all the headers the exist in every message type. Subclasses will add additional
        # headers as required.
        self._message = ""
        for line in (_request_line,
                     self._via_line,
                     self._from_line + (self._from_tag if self.from_tag is not None else ""),
                     self._to_line + (self._to_tag if self.to_tag is not None else ""),
                     self._call_id_line,
                     self._cseq_line,
                     self._contact_line,
                     self._max_forwards_line,
                     *self.additional_template_lines,
                     (self._content_type_line if self.body is not None else ""),
                     self._content_length_line,
                     (self._body if self.body is not None else "")):
            if line != "":
                self._message += line + "\n"

    def _calculate_content_length(self):
        self.content_length = len(self.sdp)

    def deconstruct(self):
        """
        Deconstruct the current SIP message into parameters of this class. Only handles parameters that are unique at
        message level. Parameters such as number and IP/port are handled at a higher scope (e.g. at dialog level).
        """
        self.content_type = self.re_content_type.match(self._message).group(0)
        self.content_length = self.re_content_length.match(self._message).group(0)
        self.subject = self.re_subject.match(self._message).group(0)
        self.max_forwards = self.re_max_forwards.match(self._message).group(0)
        self.body = self.re_body.match(self._message).group(0)


class RawSipMessage(SipMessage):
    """
    A Completely user defined message.
    """
    def __init__(self, transaction, raw_message, message_type=None):
        super().__init__(transaction, message_type)
        self.message = raw_message

    def construct_template(self):
        """
        Raw messages may not map onto the defined parameters of a Message so raw messages override the deconstructor
        """

    def deconstruct(self):
        """
        Raw messages may not map onto the defined parameters of a Message so raw messages override the constructor
        """


class Register(SipMessage):
    _expires_line = "Expires: %(registration_expiry)s"

    def __init__(self, transaction, registration_expiry=3600):
        super(Register, self).__init__(transaction, "REGISTER")
        self.registration_expiry = registration_expiry
        self.additional_template_lines.append(self._expires_line)

    def deconstruct(self):
        super(Register, self).deconstruct()
        self.registration_expiry = self.re_expires.match(self._message).group(0)


class Invite(SipMessage):
    def __init__(self, transaction):
        super(Invite, self).__init__(transaction, "INVITE")


class Trying(SipMessage):
    def __init__(self, transaction):
        super(Trying, self).__init__(transaction, "TRYING", response_number=100)


class Ringing(SipMessage):
    def __init__(self, transaction):
        super(Ringing, self).__init__(transaction, "RINGING", response_number=180)


class Ok(SipMessage):
    def __init__(self, transaction):
        super(Ok, self).__init__(transaction, "OK", response_number=200)


message_mapping = {
    "INVITE": Invite,
    "OK": Ok,
    "REGISTER": Register,
    "TRYING": Trying,
    "RINGING": Ringing
}


def parse_from_raw(transaction: Transaction, raw_message: str) -> SipMessage:
    """
    Takes a raw SIP message, finds the message type and then returns a corresponding object to represent that message
    :param transaction:
    :param raw_message:
    :return:
    """

    # Find the message type in the first line of the message. First line only because the CSeq line also matches.
    message_type = SipMessage.re_message_type.match(raw_message.split("\n")[0])

    if message_type in message_mapping.keys():
        new_message = message_mapping[message_type](transaction)
        new_message.message = raw_message
    else:
        new_message = RawSipMessage(transaction, raw_message)

    return new_message


def message_factory(transaction: Transaction, message_type: str) -> SipMessage:
    """
    Construct a message of a given type.
    :param transaction:
    :param message_type: String name of the message, must be in the message_mapping
    :return:
    """
    message_class = message_mapping[message_type]

    new_message = message_class(transaction)

    return new_message
