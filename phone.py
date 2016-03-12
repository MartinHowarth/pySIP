import re
import call
import endpoint


class Phone:
    def __init__(self):
        self.endpoint = endpoint.Endpoint("1234567890", ip="0.0.0.0", port="5060", user_agent="pySIP")

        self.calls = {}  # Call-ID : call.Call

    def receive(self, raw_message):
        """
        Takes a SIP messages, finds the call ID and passes the message to the relevant call.
        Creates a new call if Call-ID does not correlate to an existing call.
        :param str raw_message:
        """

        re_call_id = re.compile("(?:Call-ID:)\s(.*)")
        call_id = re.match(re_call_id, raw_message)

        if call_id in self.calls.keys():
            self.calls[call_id].receive(raw_message)
        else:
            re_source = re.compile("(?:From:\s)(.*)(?:\s<sip:)(.*)(?:@)(.*)(?::)(.*)(?:>.*)")
            user_agent, source_number, source_ip, source_port = re.match(re_source, raw_message)
            source_endpoint = endpoint.Endpoint(source_number, ip=source_ip, port=source_port, user_agent=user_agent)

            re_subject = re.compile("(?:Subject:)\s(.*)")
            subject = re.match(re_subject, raw_message)

            new_call = call.Call(self, source_endpoint, self.endpoint, call_id=call_id, subject=subject)
            self.calls[call_id] = new_call
