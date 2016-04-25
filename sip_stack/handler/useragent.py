from sip_stack.framework.useragent import UserAgent
from sip_stack.handler.call import CallHandler
from sip_stack.handler.better_connection import create_server
import threading
from collections import namedtuple


call_reference = namedtuple("CallReference", "call_handler thread")


class UserAgentHandler:
    def __init__(self, local_endpoint):
        self.local_endpoint = local_endpoint
        self.useragent = UserAgent()
        self.call_references = {}

        self.server = create_server(self)

        self.handle()

    def handle(self):
        pass

    def new_inbound_call(self, request_handler):
        self.new_call(request_handler.remote_endpoint, request_handler.local_endpoint, request_handler)

    def new_call(self, source_endpoint, destination_endpoint, connection=None) -> CallHandler:
        """
        Create a new call.
        If connection is not specified, then this is a call that we are originating (source_endpoint is the
            local_endpoint).
        :param source_endpoint:
        :param destination_endpoint:
        :param connection:
        :return:
        """
        call = self.useragent.new_call(source_endpoint, destination_endpoint)

        if connection is None:
            connection = create_connection(source_endpoint, destination_endpoint, self.server)

        new_call = CallHandler(call, connection)
        new_call_thread = threading.Thread(target=new_call.handle)

        self.call_references[call] = call_reference(new_call, new_call_thread)

        new_call_thread.start()
