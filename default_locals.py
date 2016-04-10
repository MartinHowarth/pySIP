import socket

from sip_stack.framework.endpoint import Endpoint

local_user_agent = "pySIP"
local_endpoint = Endpoint("3162031231", domain="example.com",
                          ip=socket.gethostbyname(socket.gethostname()), port="5060", user_agent=local_user_agent)
