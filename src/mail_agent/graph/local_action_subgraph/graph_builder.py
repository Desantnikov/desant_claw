from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END

from src.mail_agent.states.local_actions_substate import LocalActionSubState
from .models import NodesEnum
from .routing import LocalActionSubgraphRouter
from .nodes import select_action_execution_capability, execute_bash_action, execute_browser_action

local_action_subgraph_builder = StateGraph(LocalActionSubState)

# ------ NODES ------
local_action_subgraph_builder.add_node(NodesEnum.SELECT_ACTION_EXECUTION_CAPABILITY, select_action_execution_capability)

local_action_subgraph_builder.add_node(NodesEnum.EXECUTE_BROWSER_ACTION, execute_browser_action)
local_action_subgraph_builder.add_node(NodesEnum.EXECUTE_BASH_ACTION, execute_bash_action)


# ------ EDGES ------

local_action_subgraph_builder.add_edge(START, NodesEnum.SELECT_ACTION_EXECUTION_CAPABILITY)

local_action_subgraph_builder.add_conditional_edges(
    NodesEnum.SELECT_ACTION_EXECUTION_CAPABILITY,
    LocalActionSubgraphRouter.after_select_action_execution_capability,
)

local_action_subgraph = local_action_subgraph_builder.compile()

