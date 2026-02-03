from enum import Enum


class NodesEnum(str, Enum):
    ANALYZE_INPUT_SECURITY = "analyze_input_security"
    INGEST_EMAIL = "ingest_email"
    BUILD_EXECUTION_PLAN = "build_execution_plan"
    DISPATCH_EXECUTION_PLAN_STEP = "dispatch_execution_plan_step"

    SHUTDOWN = "shutdown"