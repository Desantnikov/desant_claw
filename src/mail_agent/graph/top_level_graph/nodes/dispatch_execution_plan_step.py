from src.mail_agent.shared.enums import ExecutionPlanStepTypeEnum
from src.mail_agent.shared.models import StepResult
from src.mail_agent.states.top_level_state import TopLevelState
from src.mail_agent.graph.local_action_subgraph import local_action_subgraph
from src.mail_agent.graph.reply_subgraph import reply_subgraph


async def dispatch_execution_plan_step(state: TopLevelState):
    """
        Dispatch instead of simple routing because here I want to resolve outputs from previous steps
        Subgraphs are added as a nodes to the top-level graph, so resume from checkpoint works even though
        the're called via `.invoke()`
    """
    next_step = state.execution_plan.get_next_pending_step()

    # collect artifacts to pass to the next step
    artifacts = []
    if state.step_results is not None:
        for step_index, step_result in state.step_results.items():
            artifacts.extend(step_result.artifacts)

    step_results = []
    if next_step.type == ExecutionPlanStepTypeEnum.PERFORM_LOCAL_ACTION:
        local_action_subgraph_state = await local_action_subgraph.ainvoke(
            {
                "execution_plan_step_data": next_step,
                "artifacts": artifacts,
            },
        )

        step_results = StepResult(artifacts=local_action_subgraph_state['artifacts'])

    elif next_step.type == ExecutionPlanStepTypeEnum.SEND_EMAIL:
        reply_subgraph_state = await reply_subgraph.ainvoke(
            {
                "context": state.model_dump(),
            }
        )

        step_results = StepResult(artifacts=[])

    updated_execution_plan = state.execution_plan.mark_step_completed(next_step.step_index)
    return {"execution_plan": updated_execution_plan, "step_results": {str(next_step.step_index): step_results}}