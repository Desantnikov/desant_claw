from enum import Enum

from src.mail_agent.shared.models import LocalActionCapability


class NodesEnum(str, Enum):
    SELECT_ACTION_EXECUTION_CAPABILITY = "select_action_execution_capability"

    EXECUTE_TERMINAL_ACTION = "execute_terminal_action"
    EXECUTE_BROWSER_ACTION = "execute_browser_action"

    @classmethod
    def from_capability(cls, capability: LocalActionCapability) -> "NodesEnum":
        capability_name = capability.capability_name
        for option in cls:
            if option.value == capability_name:
                return option

        # TODO: make a specific exception
        raise Exception(f"Unknown local action capability {capability_name}")



CAPABILITIES_LIST = [  # TODO: add descriptions
    LocalActionCapability(capability_name=NodesEnum.EXECUTE_BROWSER_ACTION, capability_description=None),
    LocalActionCapability(capability_name=NodesEnum.EXECUTE_TERMINAL_ACTION, capability_description=None),
]