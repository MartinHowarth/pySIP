class Endpoint:
    def __init__(self, sip_id=None, domain=None, ip=None, port=None, user_agent=None,
                 transport="UDP", via_ip=None, via_port=None):
        self.sip_id = sip_id
        self.ip = ip
        self.port = port
        self.domain = domain
        self.user_agent = user_agent

        self._via_ip = None
        self._via_port = None

        self.via_ip = via_ip
        self.via_port = via_port
        self.transport = transport

    @property
    def via_ip(self):
        return self._via_ip

    @via_ip.setter
    def via_ip(self, value):
        self._via_ip = value if value is not None else self.ip

    @property
    def via_port(self):
        return self._via_port

    @via_port.setter
    def via_port(self, value):
        self._via_port = value if value is not None else self.port
