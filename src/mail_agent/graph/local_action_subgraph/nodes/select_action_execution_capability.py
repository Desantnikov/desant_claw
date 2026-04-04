from src.mail_agent.services.action_execution_capability_selector import ActionExecutionCapabilitySelector
from src.mail_agent.services.contracts import ActionExecutionCapabilitySelectorInput
from ..models import CAPABILITIES_LIST
from src.mail_agent.states.local_actions_substate import LocalActionSubState


async def select_action_execution_capability(state: LocalActionSubState):
    available_capabilities_list = CAPABILITIES_LIST
    execution_plan_step_data = state.execution_plan_step_data

    select_action_execution_capability_input = ActionExecutionCapabilitySelectorInput(
        execution_plan_step_data=execution_plan_step_data,
        available_capabilities=available_capabilities_list
    )

    action_execution_capability_selector = ActionExecutionCapabilitySelector(select_action_execution_capability_input)
    action_execution_selected_capability = await action_execution_capability_selector.select_action_execution_capability()

    return {'selected_capability': action_execution_selected_capability}
