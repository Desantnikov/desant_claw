from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_google_community import GmailToolkit
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain.messages import HumanMessage

from settings import settings
from .contracts import SendEmailServiceInput, SendEmailServiceOutput


@dynamic_prompt
def build_step_prompt(request: ModelRequest) -> str:
    context = request.state["context"]
    return (
        "You are an email sending agent.\n"
        f"You have all the context: {context}\n"
    )


class SendEmailService:
    """
    Agentic email service for non-deterministic email
    TODO: split email generating and email send into separate services; generating via agent and sending deterministic
    """
    @staticmethod
    async def execute(input_: SendEmailServiceInput) -> SendEmailServiceOutput:
        model = ChatOpenAI(model=settings.DEFAULT_MODEL, temperature=0)
        tools = GmailToolkit().get_tools()

        agent_chain = create_agent(
            model=model,
            tools=tools,
            middleware=[build_step_prompt],
            state_schema=SendEmailServiceInput,
            response_format=SendEmailServiceOutput,
        )

        result = await agent_chain.ainvoke(
            input={
                "messages": [HumanMessage("Send an email considering all the context")],
                **input_.model_dump(),  # pass state
            },
        )
        return result["structured_response"]
