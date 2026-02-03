from pydantic import BaseModel

from src.mail_agent.shared.enums import InputSecurityStatusEnum, SenderTypeEnum
from src.mail_agent.shared.models import EmailData, ExecutionPlan


class TopLevelState(BaseModel):
    email_raw_data: dict
    email_data: EmailData | None = None
    input_security_status: InputSecurityStatusEnum | None = None
    sender_type: SenderTypeEnum | None = None
    execution_plan: ExecutionPlan | None = None