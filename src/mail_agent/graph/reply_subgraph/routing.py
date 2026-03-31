from src.mail_agent.states.local_actions_substate import LocalActionSubState

from .models import NodesEnum


class LocalActionSubgraphRouter:
    @staticmethod
    def after_select_action_execution_capability(state: LocalActionSubState):
        selected_capability = state.selected_capability

        return NodesEnum.from_capability(capability=selected_capability)
