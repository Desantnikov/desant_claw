from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser
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


class BrowserActionExecutor:
    """
    Langchain agent used here to avoid dealing with adapters on top of native
    langchain toolkits to make them work with pydantic_ai agents.
    It appeared to be not so straightforward with async tools.
    # TODO: make abstract base executor class, inherit from it; handle dynamic prompting in this base class
    """
    @staticmethod
    async def execute_async(input_: LocalActionExecutorInput) -> LocalActionExecutorOutput:
        async_browser = create_async_playwright_browser(headless=True)  # use async to avoid threading headache
        toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
        tools = toolkit.get_tools()

        model = ChatOpenAI(model="gpt-5.1", temperature=0)

        agent_chain = create_agent(
            model=model,
            tools=tools,
            middleware=[build_step_prompt],
            state_schema=LocalActionExecutorInput,
            response_format=LocalActionExecutorOutput,
        )

        result = await agent_chain.ainvoke(
            input={
                "messages": [HumanMessage("Execute current step")],
                **input_.model_dump(),  # pass state
            },
        )
        return result["structured_response"]