from sip_stack.framework.useragent import UserAgent
from sip_stack.logic.call import CallHandler


class UserAgentHandler:
    def __init__(self):
        self.useragent = UserAgent()
        self.call_handlers = {}

    def new_call(self, source_endpoint, destination_endpoint) -> CallHandler:
        call = self.useragent.new_call(source_endpoint, destination_endpoint)

        self.call_handlers[call] = CallHandler(call)
