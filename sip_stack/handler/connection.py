import socket
from sip_stack.framework.endpoint import Endpoint
from abc import ABCMeta


def create_tcp_connection(local_endpoint, remote_endpoint):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((local_endpoint.via_ip, local_endpoint.via_port))

    sock.connect((remote_endpoint.ip, remote_endpoint.port))

    return sock


def create_connection(local_endpoint, remote_endpoint, server):
    if local_endpoint.transport != remote_endpoint.transport:
        raise ValueError("Mismatched endpoint IP transport protocols")
    if local_endpoint.transport == "UDP":
        return UDPConnection(local_endpoint, remote_endpoint, server)
    elif local_endpoint.transport == "TCP":
        return TCPConnection(local_endpoint, remote_endpoint)


class Connection:
    __metaclass__ = ABCMeta

    def __init__(self, local_endpoint, remote_endpoint):
        self.local_endpoint = local_endpoint
        self.remote_endpoint = remote_endpoint

        self.listeners = []

    def register_listener(self, listening_function):
        self.listeners.append(listening_function)

    def receive_data(self, data):
        for listener in self.listeners:
            listener(data)


class TCPConnection(Connection):
    def __init__(self, local_endpoint, remote_endpoint, tcp_connection=None):
        super(TCPConnection, self).__init__(local_endpoint, remote_endpoint)

        if tcp_connection is not None:
            self._tcp_connection = tcp_connection
        else:
            self._tcp_connection = create_tcp_connection(local_endpoint, remote_endpoint)

    def listen(self):
        self.receive_data()

    def receive_data(self, buffer_size=1024):
        super(TCPConnection, self).receive_data(self._tcp_connection.recv(buffer_size))

    def send_data(self, data):
        self._tcp_connection.send(data)

    def __del__(self):
        self._tcp_connection.close()


class UDPConnection(Connection):
    def __init__(self, local_endpoint, remote_endpoint, server):
        super(UDPConnection, self).__init__(local_endpoint, remote_endpoint)
        self.udp_socket = server.listening_connection.socket

    def send_data(self, data):
        self.udp_socket.sento(data, (self.remote_endpoint.ip, self.remote_endpoint.port))


class ListeningSocket:
    def __init__(self, local_endpoint: Endpoint):
        self._local_endpoint = None
        self.socket = None
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
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self._local_endpoint.via_ip, self._local_endpoint.via_port))
        elif self._local_endpoint.transport == "TCP":
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self._local_endpoint.via_ip, self._local_endpoint.via_port))
            self.socket.listen(1)
        else:
            raise AttributeError("Unrecognised IP transport method provided.")

    @local_endpoint.deleter
    def local_endpoint(self):
        self.socket.close()

    def _parse_remote_peer(self, peer, transport):
        return Endpoint(ip=peer[0], port=peer[1], transport=transport)

    def await_tcp_connection(self):
        tcp_connection, peer = self.socket.accept()
        return tcp_connection, self._parse_remote_peer(peer, "TCP")

    def await_udp_connection(self, buffer_size=1024):
        data, peer = self.socket.recvfrom(buffer_size)
        return data, self._parse_remote_peer(peer, "UDP")


class Server:
    def __init__(self, local_endpoint: Endpoint):
        self.listening_connection = ListeningSocket(local_endpoint)
        self.tcp_peers = {}
        self.udp_peers = {}

    def await_connection(self):
        while True:
            if self.listening_connection.local_endpoint.transport == "TCP":
                tcp_connection, remote_endpoint = self.listening_connection.await_tcp_connection()
                new_connection = self.spawn_tcp_connection(tcp_connection, remote_endpoint)
                if new_connection is not None:
                    return new_connection

            elif self.listening_connection.local_endpoint.transport == "UDP":
                data, remote_endpoint = self.listening_connection.await_udp_connection(1024)
                new_connection = self.handle_udp_data(data, remote_endpoint)
                if new_connection is not None:
                    return new_connection

    def handle_udp_data(self, data, remote_endpoint):
        new_connection = False
        if remote_endpoint not in self.udp_peers.keys():
            self.udp_peers[remote_endpoint] = UDPConnection(self.listening_connection.local_endpoint, remote_endpoint)
            new_connection = True
        self.udp_peers[remote_endpoint].receive_data(data)

        if new_connection:
            return self.udp_peers[remote_endpoint]
        else:
            return None

    def spawn_tcp_connection(self, tcp_connection, remote_endpoint):
        if remote_endpoint not in self.tcp_peers.keys():
            self.tcp_peers[remote_endpoint] = TCPConnection(self.listening_connection.local_endpoint, remote_endpoint,
                                                            tcp_connection)
            return self.tcp_peers[remote_endpoint]
        else:
            # This shouldn't ever happen??
            raise Exception("Huh?")
            return None
