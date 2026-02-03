from pydantic_ai import Agent

from src.mail_agent.services.models import ExecutionPlanBuilderOutput
from src.mail_agent.shared.prompts import SYSTEM_PROMPT, EXECUTION_PLAN_BUILDER_INSTRUCTION
from src.mail_agent.shared.models import EmailData, ExecutionPlan, ExecutionPlanStep


class ExecutionPlanBuilder:
    def __init__(self, email_data: EmailData):
        self.email_data = email_data

        self.agent = Agent(
            'openai:gpt-5.1',
            system_prompt=SYSTEM_PROMPT,
            instructions=EXECUTION_PLAN_BUILDER_INSTRUCTION,
            output_type=ExecutionPlanBuilderOutput,
        )

    def build_execution_plan(self) -> ExecutionPlan:
        result = self.agent.run_sync(self.email_data.snippet)

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