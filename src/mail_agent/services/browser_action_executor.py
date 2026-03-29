from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser

from .models import BrowserActionExecutorInput


class BrowserActionExecutor:
    """
    Langchain agent used here to avoid dealing with adapters on top of native.
    langchain toolkits to make them work with pydantic_ai agents.
    It appeared to be not so straightforward with async tools.
    """
    @staticmethod
    async def execute_async(browser_action_executor_input: BrowserActionExecutorInput):
        # TODO: refactor, avoid sending plaing model dump to agent

        async_browser = create_async_playwright_browser(headless=True)
        toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
        tools = toolkit.get_tools()

        model = ChatOpenAI(model="gpt-5.1", temperature=0)

        json_dump = browser_action_executor_input.model_dump_json()
        agent_chain = create_agent(model=model, tools=tools)
        result = await agent_chain.ainvoke({"messages": [("user", json_dump)]})
        return result