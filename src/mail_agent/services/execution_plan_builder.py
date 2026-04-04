from pydantic_ai import Agent

from src.mail_agent.services.contracts import ExecutionPlanBuilderOutput
from src.mail_agent.shared.prompts import SYSTEM_PROMPT, EXECUTION_PLAN_BUILDER_INSTRUCTION
from src.mail_agent.shared.models import ExecutionPlan, ExecutionPlanStep
from src.mail_agent.shared.settings import settings
from .contracts import ExecutionPlanBuilderInput


class ExecutionPlanBuilder:
    def __init__(self, execution_plan_builder_input: ExecutionPlanBuilderInput):
        self.input = execution_plan_builder_input
        self.email_data = self.input.email_data

        self.agent = Agent(
            f'openai:{settings.DEFAULT_MODEL}',
            system_prompt=SYSTEM_PROMPT,
            instructions=EXECUTION_PLAN_BUILDER_INSTRUCTION,
            output_type=ExecutionPlanBuilderOutput,
        )

    async def build_execution_plan(self) -> ExecutionPlan:
        result = await self.agent.run(self.email_data.snippet)

        steps = []
        for index, suggested_step in enumerate(result.output.suggested_steps):
            step = ExecutionPlanStep(
                step_index=index,
                type=suggested_step.type,
                summary=suggested_step.summary,
                reason=suggested_step.reason,
                action_spec=suggested_step.action_spec,
            )
            steps.append(step)

        return ExecutionPlan(steps=steps, ordering_reason=result.output.ordering_reason)