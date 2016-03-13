class Endpoint:
    def __init__(self, number, domain=None, ip=None, port=None, user_agent=None,
                 transport="UDP", via_ip=None, via_port=None):
        self.number = number
        self.ip = ip
        self.port = port
        self.domain = domain
        self.user_agent = user_agent

        self.via_ip = via_ip if not None else ip
        self.via_port = via_port if not None else port
        self.transport = transport
