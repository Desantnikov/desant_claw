from pydantic import BaseModel, Field

from src.mail_agent.shared.models import ExecutionPlanStep
from src.mail_agent.shared.enums import ExecutionPlanStepTypeEnum
from src.mail_agent.shared.models import EmailData, LocalActionCapability


# -------------- ExecutionPlanBuilder --------------------

class ExecutionPlanBuilderInput(BaseModel):
    email_data: EmailData

class ExecutionPlanBuilderSuggestedStep(BaseModel):
    type: ExecutionPlanStepTypeEnum
    reason: str = Field(description="Reason, why this step is required")
    summary: str = Field(description="Summary of the step for the local step planner to understand substeps")
    action_spec: dict = Field(description="Machine-readable action spec")

class ExecutionPlanBuilderOutput(BaseModel):
    suggested_steps: list[ExecutionPlanBuilderSuggestedStep]
    ordering_reason: str = Field(description="Reason why these steps are planned in this exact order")
    confidence: float


# -------------- ActionExecutionNodeSelector --------------------

class ActionExecutionCapabilitySelectorInput(BaseModel):
    execution_plan_step_data: ExecutionPlanStep
    available_capabilities: list[LocalActionCapability]

class ActionExecutionCapabilitySelectorOutput(BaseModel):
    suggested_capability_name: str
    confidence: float


# -------------- BrowserActionExecutor --------------------

class BrowserActionExecutorInput(BaseModel):
    summary: str
    reason: str
    action_spec: dict