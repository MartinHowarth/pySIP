from abc import abstractmethod

from scenario.exceptions import MessageOutOfOrderException, MessageFailedVerificationException
from sip_stack.framework.message import SipMessage
from sip_stack.logic.useragent import UserAgentHandler
from default_locals import local_endpoint as _local_endpoint


class Scenario:
    """
    A scenario is a set of SIP messages to send and receive in a particular order.
    """
    def __init__(self, remote_endpoint, local_endpoint=_local_endpoint):
        self._call_handler = UserAgentHandler().new_call(local_endpoint, remote_endpoint)
        # Todo: make call handler tell us when a message has arrived

        self.queued_messages = []  # type: list[QueuedMessage]
        self._currently_expected_messages = []   # type: list[QueuedMessage]
        self._index = 0  # Current position in the scenario
        self._last_received_message = None  # type: QueuedMessage

        self.define()

    @abstractmethod
    def define(self):
        """
        Construct the scenario by calling self.send and self.expect in order.
        """

    def send(self, message: SipMessage):
        """
        Used to add a message to be sent to the scenario. Does not actually send the message when called.
        :param message: The type of SIP message to send.
        """
        self.queued_messages.append(QueuedMessage(message, outbound=True))

    def expect(self, message: SipMessage, optional: bool = False, verification_function=None):
        """
        Used to add an expected message to the scenario.
        :param message: The type of SIP message to expect.
        :param optional:
        :param function verification_function:
        """
        self.queued_messages.append(QueuedMessage(message, outbound=False, optional=optional,
                                                  verification_function=verification_function))

    def _send(self, queued_message: QueuedMessage):
        """
        Sends messages asynchronously.
        :param queued_message:
        """
        # Todo: make this asynchronous
        self._call_handler.send_message(queued_message.message)

    def _receive(self, received_message: SipMessage):
        """
        Receives messsages asynchronously.
        If the scenario definition doesn't expect the received message at this time, raise an exception.
        :param received_message:
        """
        expected_types = [message.message.type for message in self._currently_expected_messages]

        if received_message.type in expected_types:
            # Set the last received message to the corresponding QueuedMessage that we just matched by type.
            self._last_received_message = self._currently_expected_messages[expected_types.index(received_message.type)]

            if not self._last_received_message.verify_message(received_message):
                raise MessageFailedVerificationException()

            # Todo: Push self._await_message to continue
        else:
            raise MessageOutOfOrderException("Received unexpected message: %s" % received_message)

    def _await_message(self) -> SipMessage:
        """
        Blocking until a message is received in self._receive
        """
        # Todo: Implement blocking
        return

    def _calculate_expected_messages(self):
        """
        Construct a list of messsage that are valid to be next received.
        The list will include N optional messages and one non-optional message.
        It is valid for the list to be blank.
        """
        self._currently_expected_messages = []
        # Only include messages that come later in the scenario
        for queued_message in self.queued_messages[self._index:]:
            # Stop looking if we come to an inbound message
            if queued_message.outbound is False:
                self._currently_expected_messages.append(queued_message)
                # Stop looking if this is not an optional message
                if queued_message.optional is False:
                    break
            else:
                break

    def start(self):
        while self._index < len(self.queued_messages):
            next_queued_message = self.queued_messages[self._index]
            if next_queued_message.outbound:
                # Receiving is asynchronous, so we need to clear the expected queue
                self._currently_expected_messages = []
                self._send(next_queued_message)
                self._index += 1
            else:
                self._calculate_expected_messages()
                self._await_message()  # Blocking

                # Calculate the new index because we may skip some optional messages
                self._index = self.queued_messages.index(self._last_received_message) + 1


class QueuedMessage:
    def __init__(self, message: SipMessage, outbound: bool, optional: bool=False, verification_function=None):
        """

        :param message:
        :param outbound:
        :param optional:
        :param function verification_function: Should take a single parameter of type SipMessage and return a bool.
        """
        self.message = message
        self.outbound = outbound
        self.optional = optional
        self.verification_function = verification_function

    def verify_message(self, test_message: SipMessage) -> bool:
        if self.verification_function is None:
            return True

        return self.verification_function(test_message)
