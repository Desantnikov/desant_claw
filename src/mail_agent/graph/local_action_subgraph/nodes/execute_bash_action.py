from src.mail_agent.states.local_actions_substate import LocalActionSubState
from src.mail_agent.services.local_action_executors.bash_action_executor import BashActionExecutor
from src.mail_agent.services.local_action_executors.contracts import LocalActionExecutorInput


async def execute_bash_action(state: LocalActionSubState):
    step_summary = state.execution_plan_step_data.summary
    step_reason = state.execution_plan_step_data.reason
    action_spec = state.execution_plan_step_data.action_spec

    executor_service_input = LocalActionExecutorInput(
        summary=step_summary,
        reason=step_reason,
        action_spec=action_spec,
    )

    result = BashActionExecutor.execute(input_=executor_service_input)
    artifacts = result.artifacts

    return {"artifacts": artifacts}