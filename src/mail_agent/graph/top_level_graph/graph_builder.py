from langgraph.graph import StateGraph, START, END

from local_action_subgraph import local_action_subgraph
from reply_subgraph import reply_subgraph
from src.mail_agent.states.top_level_state import TopLevelState

from .routing import TopLevelRouter
from .models import NodesEnum
from .nodes import debug_print, shutdown, ingest_email, analyze_input_security, build_execution_plan, dispatch_execution_plan_step

graph_builder = StateGraph(TopLevelState)

# ------ NODES ------
graph_builder.add_node(NodesEnum.INGEST_EMAIL, ingest_email)
graph_builder.add_node(NodesEnum.ANALYZE_INPUT_SECURITY, analyze_input_security)
graph_builder.add_node(NodesEnum.BUILD_EXECUTION_PLAN, build_execution_plan)
graph_builder.add_node(NodesEnum.DISPATCH_EXECUTION_PLAN_STEP, dispatch_execution_plan_step)
# add subgraphs as nodes so they share same checkpointer for HITL
graph_builder.add_node(NodesEnum.LOCAL_ACTION_SUBGRAPH, local_action_subgraph)
graph_builder.add_node(NodesEnum.REPLY_SUBGRAPH, reply_subgraph)

graph_builder.add_node(NodesEnum.SHUTDOWN, shutdown)
graph_builder.add_node('debug_print', debug_print)


# ------ EDGES ------
graph_builder.add_edge(NodesEnum.SHUTDOWN, END)  # graph should be finished only through the shutdown node

# graph start
graph_builder.add_edge(START, NodesEnum.INGEST_EMAIL)
graph_builder.add_edge(NodesEnum.INGEST_EMAIL, NodesEnum.ANALYZE_INPUT_SECURITY)
graph_builder.add_conditional_edges(
    NodesEnum.ANALYZE_INPUT_SECURITY,  # if security ok --> BUILD_EXECUTION_PLAN
    TopLevelRouter.after_analyze_input_security,  # else --> SHUTDOWN
)
graph_builder.add_edge(NodesEnum.BUILD_EXECUTION_PLAN, NodesEnum.DISPATCH_EXECUTION_PLAN_STEP)

graph_builder.add_conditional_edges(
    NodesEnum.DISPATCH_EXECUTION_PLAN_STEP,  # if > 0 PENDING steps ---> DISPATCH again
    TopLevelRouter.after_dispatch_execution_plan,  # else SHUTDOWN
)

# TODO: move compilation to GraphRuntime
async def compile_graph(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)

