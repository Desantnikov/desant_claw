import re

from src.mail_agent.shared.enums import SenderTypeEnum
from src.mail_agent.states.top_level_state import TopLevelState
from src.mail_agent.shared.models import EmailData
from src.mail_agent.shared.settings import settings


EMAIL_REGEXP = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"


async def ingest_email(state: TopLevelState):
    mails_found = re.findall(EMAIL_REGEXP, state.email_raw_data['sender'])
    snippet_text = state.email_raw_data['snippet']  # TODO: decode text

    email_data = EmailData(
        sender_address=mails_found[0],
        snippet=snippet_text,
    )

    sender_type = SenderTypeEnum.EXTERNAL
    if email_data.sender_address == settings.INTERNAL_EMAIL_ADDRESS:
        sender_type = SenderTypeEnum.INTERNAL

    return {"email_data": email_data, "sender_type": sender_type}