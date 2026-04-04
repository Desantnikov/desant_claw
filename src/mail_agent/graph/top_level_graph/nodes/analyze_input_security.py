from src.mail_agent.states.top_level_state import TopLevelState
from src.mail_agent.shared.enums import InputSecurityStatusEnum


async def analyze_input_security(state: TopLevelState):
    # TODO: analyze somehow
    return {'input_security_status': InputSecurityStatusEnum.CLEAN}

