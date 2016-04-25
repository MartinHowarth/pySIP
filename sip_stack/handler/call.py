from sip_stack.framework.message import SipMessage
from sip_stack.framework.call import Call
from sip_stack.handler.connection import Connection


class CallHandler:
    def __init__(self, call: Call, connection: Connection):
        self.call = call
        self.connection = connection
        self.connection.register_listener(self.receive_data)

        self.data_buffer = ""

    def send_message(self, message_type: SipMessage):
        """
        Construct the SIP message and add it into the call framework. Then actually send the message.
        :param message_type: Type of SIP message to send
        :return:
        """
        new_message = self.call.new_message(message_type)

    def receive_data(self, data: str):
        """
        Receives data asynchronously.
        :param data:
        """
        self.data_buffer += data

    def handle(self):
        """
        Do the work of handling a call.
        """
        while True:
            pass
