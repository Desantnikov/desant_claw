from src.mail_agent.services.execution_plan_builder import ExecutionPlanBuilder
from src.mail_agent.services.models import ExecutionPlanBuilderInput
from src.mail_agent.states.top_level_state import TopLevelState


def build_execution_plan(state: TopLevelState):
    execution_plan_builder_input = ExecutionPlanBuilderInput(email_data=state.email_data)
    execution_plan_builder = ExecutionPlanBuilder(execution_plan_builder_input)
    execution_plan = execution_plan_builder.build_execution_plan()

    return {'execution_plan': execution_plan}
