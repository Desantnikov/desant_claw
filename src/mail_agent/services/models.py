from pydantic import BaseModel, Field

from src.mail_agent.shared.enums import ExecutionPlanStepTypeEnum


class ExecutionPlanBuilderSuggestedStep(BaseModel):
    type: ExecutionPlanStepTypeEnum
    reason: str = Field(description="Reason, why this step is required")
    summary: str = Field(description="Summary of the step for the local step planner to understand substeps")
    action_spec: dict = Field(description="Machine-readable action spec")

class ExecutionPlanBuilderOutput(BaseModel):
    suggested_steps: list[ExecutionPlanBuilderSuggestedStep]
    ordering_reason: str = Field(description="Reason why these steps are planned in this exact order")
    confidence: float