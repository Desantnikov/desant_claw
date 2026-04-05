from src import utils
from src.settings import settings
from src.mail_agent.shared.enums import SenderTypeEnum
from src.mail_agent.states.top_level_state import TopLevelState
from src.mail_agent.shared.models import EmailData


async def ingest_email(state: TopLevelState):
    sender_email = utils.parse_email(input_string=state.email_raw_data['sender'])
    snippet_text = state.email_raw_data['snippet']  # TODO: decode text

    email_data = EmailData(
        sender_address=sender_email,
        snippet=snippet_text,
    )

    sender_type = SenderTypeEnum.EXTERNAL
    if email_data.sender_address == settings.INTERNAL_EMAIL_ADDRESS:
        sender_type = SenderTypeEnum.INTERNAL

    return {"email_data": email_data, "sender_type": sender_type}