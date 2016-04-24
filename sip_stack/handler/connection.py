import socket
from sip_stack.framework.endpoint import Endpoint


class Connection:
    def __init__(self, local_endpoint, remote_endpoint):
        self.local_endpoint = local_endpoint
        self.remote_endpoint = remote_endpoint


class TCPConnection(Connection):
    def __init__(self, local_endpoint, remote_endpoint, tcp_connection):
        super(TCPConnection, self).__init__(local_endpoint, remote_endpoint)
        self._tcp_connection = tcp_connection

        self.listen()

    def listen(self):
        while True:
            self.receive_data()

    def receive_data(self, buffer_size=1024):
        return self._tcp_connection.recv(buffer_size)

    def __del__(self):
        self._tcp_connection.close()


class UDPConnection(Connection):
    def __init__(self, local_endpoint, remote_endpoint):
        super(UDPConnection, self).__init__(local_endpoint, remote_endpoint)

    def receive_data(self, data):
        return data


class ListeningSocket:
    def __init__(self, local_endpoint: Endpoint):
        self._local_endpoint = None
        self._socket = None
        self._tcp_connection = None
        self._tcp_peer_ip = None

        self.local_endpoint = local_endpoint

    @property
    def local_endpoint(self):
        return self._local_endpoint

    @local_endpoint.setter
    def local_endpoint(self, value):
        self._local_endpoint = value
        if self._local_endpoint.transport == "UDP":
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.bind((self._local_endpoint.via_ip, self._local_endpoint.via_port))
        elif self._local_endpoint.transport == "TCP":
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.bind((self._local_endpoint.via_ip, self._local_endpoint.via_port))
            self._socket.listen(1)
        else:
            raise AttributeError("Unrecognised IP transport method provided.")

    @local_endpoint.deleter
    def local_endpoint(self):
        self._socket.close()

    def _parse_remote_peer(self, peer, transport):
        return Endpoint(ip=peer[0], port=peer[1], transport=transport)

    def await_tcp_connection(self):
        tcp_connection, peer = self._socket.accept()
        return tcp_connection, self._parse_remote_peer(peer, "TCP")

    def await_udp_connection(self, buffer_size=1024):
        data, peer = self._socket.recvfrom(buffer_size)
        return data, self._parse_remote_peer(peer, "UDP")


class Server:
    def __init__(self, local_endpoint: Endpoint):
        self.listening_connection = ListeningSocket(local_endpoint, None, False)
        self.tcp_peers = {}
        self.udp_peers = {}

        self.listen()

    def listen(self):
        while True:
            if self.listening_connection.local_endpoint.transport == "TCP":
                tcp_connection, remote_endpoint = self.listening_connection.await_tcp_connection()
                self.spawn_tcp_connection(tcp_connection, remote_endpoint)
            elif self.listening_connection.local_endpoint.transport == "UDP":
                data, remote_endpoint = self.listening_connection.await_udp_connection(1024)
                self.handle_udp_data(data, remote_endpoint)

    def handle_udp_data(self, data, remote_endpoint):
        if remote_endpoint not in self.udp_peers.keys():
            self.udp_peers[remote_endpoint] = UDPConnection(self.listening_connection.local_endpoint, remote_endpoint)
        self.udp_peers[remote_endpoint].receive_data(data)

    def spawn_tcp_connection(self, tcp_connection, remote_endpoint):
        # Todo: Spawn TCP connection in it's own thread.
        if remote_endpoint not in self.tcp_peers.keys():
            self.tcp_peers[remote_endpoint] = TCPConnection(self.listening_connection.local_endpoint, remote_endpoint,
                                                            tcp_connection)
