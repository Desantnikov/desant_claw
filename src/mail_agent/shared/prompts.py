SYSTEM_PROMPT = """
    You are an AI assistant.
    You must be concise.
    Always return structured JSON.
"""

EXECUTION_PLAN_BUILDER_INSTRUCTION = """
    Analyze the email and decide which actions are required.
    If action require another action to be done - plan the required action too.
    Take into account possible consequences of the steps.
    Considering step consequences place steps in order which allows all the steps to be executed and the task to be completed.
    Split steps into atomic actions.
    Do NOT split action spec into substeps. If you need to split them into substeps. Generate a general
    step overview suitable for passing to another specific LLM agent.
    Return execution plan as JSON.
"""

ACTION_EXECUTION_NODE_SELECTOR_INSTRUCTION = """
    Analyze the provided execution plan step data and decide which capability should be used to perform required action.
    Use ONLY capabilities from the available capabilities.
    Chose ONE capability from the available capabilities.
    Do NOT invent any new capabilities not listed in the available capabilities.
    Return only the capability name.
"""