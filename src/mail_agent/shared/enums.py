from enum import Enum


class SenderTypeEnum(str, Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"


class InputSecurityStatusEnum(str, Enum):
    CLEAN = "clean"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"


class ExecutionPlanStepTypeEnum(str, Enum):
    PERFORM_LOCAL_ACTION = "perform_local_action"
    SEND_EMAIL = "send_email"
    DO_NOTHING = "do_nothing"


class ExecutionPlanStepStatusEnum(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

