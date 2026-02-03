from langgraph.graph import StateGraph, START, END

from src.mail_agent.states.local_actions_substate import LocalActionSubState
from .models import NodesEnum
from .nodes import perform_local_action

local_action_subgraph_builder = StateGraph(LocalActionSubState)

# ------ NODES ------
local_action_subgraph_builder.add_node(NodesEnum.PERFORM_LOCAL_ACTION, perform_local_action)

# ------ EDGES ------
local_action_subgraph_builder.add_edge(START, NodesEnum.PERFORM_LOCAL_ACTION)



local_action_subgraph = local_action_subgraph_builder.compile()
