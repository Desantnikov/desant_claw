from langgraph.graph import StateGraph, START, END

from src.mail_agent.states.reply_substate import ReplySubState
from .models import NodesEnum
from .nodes import send_email

reply_subgraph_builder = StateGraph(ReplySubState)

# ------ NODES ------
reply_subgraph_builder.add_node(NodesEnum.SEND_EMAIL, send_email)

# ------ EDGES ------
reply_subgraph_builder.add_edge(START, NodesEnum.SEND_EMAIL)


reply_subgraph = reply_subgraph_builder.compile()
