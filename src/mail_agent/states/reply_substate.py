from typing import List

from pydantic import BaseModel



class ReplySubState(BaseModel):
    # text: str | None = None
    # risk_status: str | None = None
    # approved_by_human: bool | None = None
    # status: str | None = None
    # result: str | None = None
    # errors: List[str] | None = None
    context: dict
    result: dict | None = None