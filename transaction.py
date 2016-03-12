class Transaction:
    def __init__(self):

        self.local_ip = "0.0.0.0"
        self.local_port = 5060
        self.remote_port = 5060
        self.branch = "z9hG4bK"
        self.destination_number = "1234567890"
        self.source_number = "1234567890"
        self.domain = "example.com"
        self.call_id = ""
        self.user_agent = "pySIP"
        self.subject = "Default"
        self.content_type = "application/sdp"
        self.content_length = 0
        self.transport = "UDP"
        self.sdp = ""

    def send(self, message):
        """
        :param message.Message message:
        """
        message.local_ip = self.local_ip
        message.local_port = self.local_port
        message.remote_port = self.remote_port
        message.destination_number = self.destination_number
        message.source_number = self.source_number
        message.domain = self.domain
        message.branch = self.branch
        message.user_agent = self.user_agent

        print(message.message)

