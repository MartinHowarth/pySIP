class Endpoint:
    def __init__(self, sip_id, domain=None, ip=None, port=None, user_agent=None,
                 transport="UDP", via_ip=None, via_port=None):
        self.sip_id = sip_id
        self.ip = ip
        self.port = port
        self.domain = domain
        self.user_agent = user_agent

        self.via_ip = via_ip if via_ip is not None else ip
        self.via_port = via_port if via_port is not None else port
        self.transport = transport
