from pydantic import BaseModel


class LocalActionSubState(BaseModel):
    action_spec: dict
    reason: str
    summary: str
    result: dict | None = None