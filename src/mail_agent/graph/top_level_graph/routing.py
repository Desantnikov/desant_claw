from src.mail_agent.states.top_level_state import TopLevelState

from .models import NodesEnum
from ...shared.enums import InputSecurityStatusEnum


class TopLevelRouter:
    @staticmethod
    def after_analyze_input_security(state: TopLevelState):
        if state.input_security_status in [InputSecurityStatusEnum.CLEAN, InputSecurityStatusEnum.SUSPICIOUS]:
            return NodesEnum.BUILD_EXECUTION_PLAN

        return NodesEnum.SHUTDOWN

    @staticmethod
    def after_dispatch_execution_plan(state: TopLevelState):
        if state.execution_plan.get_next_pending_step() is None:
            return NodesEnum.SHUTDOWN

        return NodesEnum.DISPATCH_EXECUTION_PLAN_STEP