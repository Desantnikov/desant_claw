from src.mail_agent.states.top_level_state import TopLevelState

from .analyze_input_security import analyze_input_security
from .build_execution_plan import build_execution_plan
from .ingest_email import ingest_email
from .dispatch_execution_plan_step import dispatch_execution_plan_step

from .shutdown import shutdown


def debug_print(state: TopLevelState):
    print('DEBUG PRINT CALLED')