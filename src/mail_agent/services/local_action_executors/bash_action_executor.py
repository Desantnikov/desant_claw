from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_community.tools.shell import ShellTool
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain.messages import HumanMessage

from .contracts import LocalActionExecutorInput, LocalActionExecutorOutput


@dynamic_prompt
def build_step_prompt(request: ModelRequest) -> str:
    summary = request.state["summary"]
    reason = request.state["reason"]
    action_spec = request.state["action_spec"]

    return (
        "You are a browser action execution agent.\n"
        f"Required step summary: {summary}\n"
        f"Reason (why this step is required): {reason}\n"
        f"Action spec: {action_spec}\n"
    )


class BashActionExecutor:
    """
    Langchain agent used here to avoid dealing with adapters on top of native
    langchain toolkits to make them work with pydantic_ai agents.
    It appeared to be not so straightforward with async tools.
    # TODO: make abstract base executor class, inherit from it; handle dynamic prompting in this base class
    """
    @staticmethod
    def execute(input_: LocalActionExecutorInput) -> LocalActionExecutorOutput:
        model = ChatOpenAI(model="gpt-5.1", temperature=0)
        tools = [ShellTool()]

        agent_chain = create_agent(
            model=model,
            tools=tools,
            middleware=[build_step_prompt],
            state_schema=LocalActionExecutorInput,
            response_format=LocalActionExecutorOutput,
        )

        result = agent_chain.invoke(
            input={
                "messages": [HumanMessage("Execute current step")],
                **input_.model_dump(),  # pass state
            },
        )
        return result["structured_response"]