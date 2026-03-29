import asyncio

from src.mail_agent.states.local_actions_substate import LocalActionSubState
from src.mail_agent.services.browser_action_executor import BrowserActionExecutor
from src.mail_agent.services.models import BrowserActionExecutorInput


def execute_browser_action(state: LocalActionSubState):
    step_summary = state.execution_plan_step_data.summary
    step_reason = state.execution_plan_step_data.reason
    action_spec = state.execution_plan_step_data.action_spec

    browser_action_executor_input = BrowserActionExecutorInput(
        summary=step_summary,
        reason=step_reason,
        action_spec=action_spec,
    )

    result = asyncio.run(BrowserActionExecutor.execute_async(browser_action_executor_input=browser_action_executor_input))

    return {"result": {"blabla": "blabla"}}