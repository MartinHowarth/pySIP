from sip_stack.framework.useragent import UserAgent
from sip_stack.handler.call import CallHandler
from sip_stack.handler.connection import Server, UDPConnection, TCPConnection


class UserAgentHandler:
    def __init__(self):
        self.useragent = UserAgent()
        self.call_handlers = {}

        self.server = None

    def new_server(self, local_endpoint):
        self.server = Server(local_endpoint=local_endpoint)

    def new_call(self, source_endpoint, destination_endpoint) -> CallHandler:
        call = self.useragent.new_call(source_endpoint, destination_endpoint)
        
        # Todo: Create connection
        connection = None

        self.call_handlers[call] = CallHandler(call, connection)
