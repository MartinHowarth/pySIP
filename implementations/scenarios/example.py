from scenario.scenario_handler import Scenario
from sip_stack.framework.message import Register, Ok


class ExampleScenario(Scenario):
    def define(self):
        self.send(Register)
        self.expect(Ok)
