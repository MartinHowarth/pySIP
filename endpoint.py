class Endpoint:
    def __init__(self, number, domain=None, ip=None, port=None, user_agent=None):
        self.number = number
        self.ip = ip
        self.port = port
        self.domain = domain
        self.user_agent = user_agent
