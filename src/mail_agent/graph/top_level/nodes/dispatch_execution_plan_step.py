from src.mail_agent.shared.models import StepResult
from src.mail_agent.states.top_level_state import TopLevelState
from src.mail_agent.graph.local_action_subgraph import local_action_subgraph


def dispatch_execution_plan_step(state: TopLevelState):
    """
    # dispatch instead of simple routing because here I want to resolve outputs from previous steps
    # TODO: resolve previous node output to state
    """
    next_step = state.execution_plan.get_next_pending_step()

    local_action_subgraph_state = local_action_subgraph.invoke({"execution_plan_step_data": next_step})

    step_results = StepResult(artifacts=local_action_subgraph_state['artifacts'])
    updated_execution_plan = state.execution_plan.mark_step_completed(next_step.step_index)
    return {"execution_plan": updated_execution_plan, "step_results": {str(next_step.step_index): step_results}}