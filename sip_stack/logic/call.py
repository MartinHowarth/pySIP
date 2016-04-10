from sip_stack.framework.message import SipMessage
from sip_stack.framework.call import Call


class CallHandler:
    def __init__(self, call: Call):
        self.call = call
        # Todo: implement listeners to notify when messages are sent and received

    def send_message(self, message_type: SipMessage):
        """
        Construct the SIP message and add it into the call framework. Then actually send the message.
        :param message_type: Type of SIP message to send
        :return:
        """

        pass
