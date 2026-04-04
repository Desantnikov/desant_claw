import asyncio

from src.mail_agent.states.local_actions_substate import LocalActionSubState
from src.mail_agent.services.local_action_executors.browser_action_executor import BrowserActionExecutor
from src.mail_agent.services.local_action_executors.contracts import LocalActionExecutorInput


async def execute_browser_action(state: LocalActionSubState):
    step_summary = state.execution_plan_step_data.summary
    step_reason = state.execution_plan_step_data.reason
    action_spec = state.execution_plan_step_data.action_spec

    executor_service_input = LocalActionExecutorInput(
        summary=step_summary,
        reason=step_reason,
        action_spec=action_spec,
    )

    result = await BrowserActionExecutor.execute_async(input_=executor_service_input)
    artifacts = result.artifacts

    return {"artifacts": artifacts}