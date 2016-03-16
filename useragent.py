import re
import call
import endpoint


class UserAgent:
    re_source = re.compile("(?:From:\s)(.*)(?:\s<sip:)(.*)(?:@)(.*)(?::)(.*)(?:>.*)")
    re_via = re.compile("(?:Via:\sSIP\/2.0\/)(.*)[ ](.*)(?::)(.*)(?:;.*)")
    re_subject = re.compile("(?:Subject:)\s(.*)")

    def __init__(self):
        self.endpoint = endpoint.Endpoint("1234567890", ip="0.0.0.0", port="5060", user_agent="pySIP")

        self.calls = {}  # Call-ID : call.Call

    def new_call(self, source_endpoint, destination_endpoint, call_id=None, subject=None):
        new_call = call.Call(self, source_endpoint, destination_endpoint, call_id=call_id, subject=subject)
        self.calls[new_call.call_id] = new_call

    def parse_message(self, raw_message):
        """
        Takes a SIP messages, finds the call ID and passes the message to the relevant call.
        Creates a new call if Call-ID does not correlate to an existing call.
        :param str raw_message:
        """

        re_call_id = re.compile("(?:Call-ID:)\s(.*)")
        call_id = re.match(re_call_id, raw_message)

        if call_id in self.calls.keys():
            self.calls[call_id].parse_message(raw_message)
        else:
            # We're receiving a new call, so we are the destination endpoint.
            user_agent, source_number, source_ip, source_port = self.re_source.match(raw_message).groups()
            transport, via_ip, via_port = self.re_via.match(raw_message).groups()
            source_endpoint = endpoint.Endpoint(source_number, ip=source_ip, port=source_port, user_agent=user_agent,
                                                transport=transport, via_ip=via_ip, via_port=via_port)
            subject = self.re_subject.match(raw_message).group(0)

            self.new_call(source_endpoint, self.endpoint, call_id=call_id, subject=subject)
            self.calls[call_id].parse_message(raw_message)
