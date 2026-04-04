from src.mail_agent.services.send_email_service import SendEmailService
from src.mail_agent.services.contracts import SendEmailServiceInput
from src.mail_agent.states.reply_substate import ReplySubState


async def send_email(state: ReplySubState):
    send_email_service_input = SendEmailServiceInput(context=state.context)
    send_email_service_result = await SendEmailService.execute(input_=send_email_service_input)

    return {'result': send_email_service_result}
