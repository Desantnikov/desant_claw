from pydantic_ai import Agent

from src.mail_agent.services.contracts import ActionExecutionCapabilitySelectorInput, ActionExecutionCapabilitySelectorOutput
from src.mail_agent.shared.prompts import SYSTEM_PROMPT, ACTION_EXECUTION_NODE_SELECTOR_INSTRUCTION
from src.mail_agent.shared.models import LocalActionCapability
from src.mail_agent.shared.exceptions import ServiceException
from src.mail_agent.shared.settings import settings


class ActionExecutionCapabilitySelector:
    """
    Takes available capabilities, intent, and selects the most suitable one
    List of available capabilities is taken from (but not limited by) the list of execution nodes from action subgraph
    """
    def __init__(self, action_execution_capability_selector_input: ActionExecutionCapabilitySelectorInput):
        self.input = action_execution_capability_selector_input
        self.execution_plan_step_data = self.input.execution_plan_step_data
        self.available_capabilities = self.input.available_capabilities

        self.agent = Agent(
            f'openai:{settings.DEFAULT_MODEL}',
            system_prompt=SYSTEM_PROMPT,
            instructions=ACTION_EXECUTION_NODE_SELECTOR_INSTRUCTION,
            output_type=ActionExecutionCapabilitySelectorOutput,
        )

    async def select_action_execution_capability(self) -> LocalActionCapability:
        # TODO: add capabilities injection to instruction via @agent.instructions
        result = await self.agent.run(
            f"Execution plan step data: {self.execution_plan_step_data};\r\n"
            f"List of available capabilities: {self.available_capabilities}",
        )

        suggested_capability_name = result.output.suggested_capability_name

        for capability in self.available_capabilities:
            if capability.capability_name == suggested_capability_name:
                return capability

        raise ServiceException()   # TODO: make exceptions more verbose
