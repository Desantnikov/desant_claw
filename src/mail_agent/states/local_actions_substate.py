from pydantic import BaseModel

from src.mail_agent.shared.models import ExecutionPlanStep, LocalActionCapability


class LocalActionSubState(BaseModel):
    execution_plan_step_data: ExecutionPlanStep
    selected_capability: LocalActionCapability | None = None
    result: dict | None = None