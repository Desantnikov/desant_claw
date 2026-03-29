from src.mail_agent.states.local_actions_substate import LocalActionSubState
from src.mail_agent.services.browser_action_executor import BrowserActionExecutor

import asyncio




def execute_terminal_action(state: LocalActionSubState):
    # local_action_executor = LocalActionExecutor().execute()

    asyncio.run(BrowserActionExecutor.execute_async())

    return {"result": {"blabla": "blabla"}}