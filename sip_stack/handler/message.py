from sip_stack.framework.message import SipMessage


class MessageHandler:
    def __init__(self, message: SipMessage):
        self.message = message

