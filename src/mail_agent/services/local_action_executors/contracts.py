from pydantic import BaseModel

from src.mail_agent.shared.models import Artifact

"""
All executor services share same interface
"""


class LocalActionExecutorInput(BaseModel):
    summary: str
    reason: str
    action_spec: dict


class LocalActionExecutorOutput(BaseModel):
    artifacts: list[Artifact]