from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain.agents.middleware import dynamic_prompt, ModelRequest, HumanInTheLoopMiddleware, InterruptOnConfig
from langchain.messages import HumanMessage
from playwright.async_api import async_playwright

from .contracts import LocalActionExecutorInput, LocalActionExecutorOutput
from src.mail_agent.shared.settings import settings

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
    # """
    @staticmethod
    async def execute_async(input_: LocalActionExecutorInput) -> LocalActionExecutorOutput:
        """
        Not using create_async_playwright_browser from langchain_community bcs it leads to unexpected behaviour
        """
        playwright_instance = await async_playwright().start()
        async_browser = await playwright_instance.chromium.launch(headless=True)

        try:
            toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
            tools = toolkit.get_tools()

            model = ChatOpenAI(model=settings.DEFAULT_MODEL, temperature=0)

            agent_chain = create_agent(
                model=model,
                tools=tools,
                middleware=[
                    build_step_prompt,
                    HumanInTheLoopMiddleware(
                        interrupt_on={
                            "navigate_browser": True,  # All decisions (approve, edit, reject) allowed
                        },
                        # Prefix for interrupt messages - combined with tool name and args to form the full message
                        # e.g., "Tool execution pending approval: execute_sql with query='DELETE FROM...'"
                        # Individual tools can override this by specifying a "description" in their interrupt config
                        description_prefix="Tool execution pending approval",
                    ),
                ],
                state_schema=LocalActionExecutorInput,
                response_format=LocalActionExecutorOutput,
            )

            result = await agent_chain.ainvoke(
                input={
                    "messages": [HumanMessage("Execute current step")],
                    **input_.model_dump(),  # pass state
                },
            )
            #
            # from langgraph.types import interrupt
            # approved = interrupt("Do you approve this action?")

            return result["structured_response"]

        finally:
            await async_browser.close()
            await playwright_instance.stop()
