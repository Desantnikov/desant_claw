from langgraph.types import Command

from .models import Event, EventType
from ..graph.top_level_graph.graph_builder import compile_graph
from ..graph.persistence.async_checkpointer import create_async_checkpointer


class GraphRuntime:
    def __init__(self):
        self.graph = None

    async def process_event(self, event: Event):
        checkpointer = await create_async_checkpointer()  # TODO: use `get` instead of `create`; add .setup()
        self.graph = await compile_graph(checkpointer=checkpointer)

        # thread_id is set during the Event creation, either a new one (new run) or an existing one (continue)
        graph_config = {"configurable": {"thread_id": event.thread_id}}

        if event.type == EventType.NEW_REQUEST:
            graph_input = {"email_raw_data": event.content}
        elif event.type == EventType.HITL_RESPONSE:
            graph_input = Command(resume={"decisions": event.decisions})
        else:
            raise Exception("Unknown event type")

        return await self.graph.ainvoke(input=graph_input, config=graph_config)