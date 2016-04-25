import socketserver
from sip_stack.framework.endpoint import Endpoint


def create_server(user_agent_handler):
    local_endpoint = user_agent_handler.local_endpoint
    if local_endpoint.transport == "TCP":
        server = socketserver.ThreadingTCPServer((local_endpoint.ip, local_endpoint.port), TCPRequestHandler)
    elif local_endpoint.transport == "UDP":
        server = socketserver.ThreadingUDPServer((local_endpoint.ip, local_endpoint.port), UDPRequestHandler)
    else:
        raise AttributeError("Invalid IP transport type: %s" % local_endpoint.transport)
    server.user_agent_handler = user_agent_handler
    return server


class MyBaseRequestHandler(socketserver.BaseRequestHandler):
    def __init__(self, *args, **kwargs):
        super(MyBaseRequestHandler, self).__init__(*args, **kwargs)
        self.local_endpoint = Endpoint(ip=self.client_address[0],
                                       port=self.client_address[1])
        self.remote_endpoint = Endpoint()

        self.user_agent_handler = None

    def calculate_remote_endpoint(self):
        self.remote_endpoint.ip = self.client_address[0]
        self.remote_endpoint.port = self.client_address[1]


class TCPRequestHandler(MyBaseRequestHandler):
    def __init__(self, *args, **kwargs):
        super(TCPRequestHandler, self).__init__(*args, **kwargs)
        self.local_endpoint.transport = "TCP"
        self.remote_endpoint.transport = "TCP"

    def handle(self):
        self.calculate_remote_endpoint()
        self.user_agent_handler.new_inbound_call(self)

    def receive_data(self):
        data = str(self.request.recv(1024), 'ascii')

    def send_data(self, data: str):
        self.request.sendall(bytes(data))


class UDPRequestHandler(MyBaseRequestHandler):
    def __init__(self, *args, **kwargs):
        super(UDPRequestHandler, self).__init__(*args, **kwargs)
        self.local_endpoint.transport = "UDP"
        self.remote_endpoint.transport = "UDP"

    def handle(self):
        self.calculate_remote_endpoint()
        self.user_agent_handler.new_inbound_call(self)

    def receive_data(self):
        data = self.request[0].strip()
        socket = self.request[1]
        remote_ip = self.client_address[0]
        remote_port = self.client_address[1]

    def send_data(self, data: str, target_ip, target_port):
        socket.sendto(data, (target_ip, target_port))
