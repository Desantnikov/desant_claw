from pydantic import BaseModel

from .enums import ExecutionPlanStepStatusEnum, ExecutionPlanStepTypeEnum

class EmailData(BaseModel):
    sender_address: str
    snippet: str


class ExecutionPlanStep(BaseModel):
    status: ExecutionPlanStepStatusEnum = ExecutionPlanStepStatusEnum.PENDING

    type: ExecutionPlanStepTypeEnum
    step_index: int
    summary: str
    reason: str
    action_spec: dict

    errors: list[str] | None = []


class ExecutionPlan(BaseModel):
    ordering_reason: str

    steps: list[ExecutionPlanStep]

    def get_next_pending_step(self) -> ExecutionPlanStep | None:
        pending_steps = list(filter(lambda step: step.status == ExecutionPlanStepStatusEnum.PENDING, self.steps))
        if pending_steps:
            return pending_steps[0]
        return None

    def mark_step_completed(self, step_index: int) -> "ExecutionPlan":
        """ Since state should be immutable but we need to mark step as completed - recreate the whole plan """
        completed_step = self.steps[step_index].model_copy(update={"status": ExecutionPlanStepStatusEnum.COMPLETED})

        updated_steps = self.steps.copy()
        updated_steps[step_index] = completed_step

        updated_execution_plan = self.model_copy(update={"steps": updated_steps})

        return updated_execution_plan


class LocalActionCapability(BaseModel):
    capability_name: str
    capability_description: str | None = None  # TODO: descriptions
