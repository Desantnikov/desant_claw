curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"



1. ingest_email (adds normalized email data to state)
2. analyze_input_security (adds "security_score: secure/suspicious/malicious")
3. shutdown (if not secure)
4. build_execution_plan (adds "execution_plan: [send_reply, perform_local_action])
    also add deterministic validation node
5. evaluate_execution_plan ()
6. execute_planned_step (decides to which node to go in the next step)
7. local_action (not a node, but a subgraph, executed for each local action from plan)
   7.1 perform_local_action (adds result to the substate)
8. reply (not a node, but subgraph)
    5.1 generate_reply (considering "local_actions_result" data from state, adds "generated_reply" to state)
    5.2 identify_risks (adds "risk_score" to state)
    5.3 request_email_reply_human_approval (adds "reply_approved" to state)
    5.4 send_email (add result to state)
 
For planning and other one-shot actions pydantic_ai agents are used
For agent loops langgraph agents are used

 ingest_email -> build_execution_plan -> validate_execution_plan
 -> execute_planned_step
 
 CHECK execution_plan and execution_plan_results
 IF action IN execution_plan AND in execution_plan_results: SKIP
 ELSE (depending on the next action in execution_plan)
 -> local_action subgraph
 OR
 -> reply subgraph
 
 
 
 State:
    mail_raw_data
 	mail_ingested_data
 	input_security_status
 	sender_type
 	execution_plan
 		steps
	 		type
	 		status
	 		reason
	 		errors
 		
 	local_actions_substate
 		steps
 			security_status
	 		approved_by_human
	 		status
	 		result
	 		errors
 		
 	reply_substate
 		text
 		risk_status
 		approved_by_human
 		status
 		result
 		errors


src
- mail_agent
- - shared
- - - models.py
- - - constants.py
- - - enums.py
- - services
- - - models.py
- - - mail_service.py
- - - execution_plan_builder.py (top-level)
- - - action_execution_node_selector.py (for action subgraph)
- - - browser_action_executor.py
- - - <all_services_files>
- - states
- - - top_level_state.py
- - - reply_substate.py
- - - local_actions_substate.py
- - graph
- - - top_level
- - - - models.py (with NodesEnum)
- - - - routing.py
- - - - graph_builder.py
- - - - nodes
- - - - - ingest_mail.py
- - - - - analyze_input_security.py
- - - - - <all_other_top_level_nodes>
- - - local_actions_subgraph
- - - - routing.py
- - - - graph_builder.py
- - - - models.py (with NodesEnum)
- - - - nodes
- - - - - execute_browser_action.py
- - - - - <all_remaining_action_types>
- - - reply_subgraph
- - - - models.py (with NodesEnum)
- - - - routing.py
- - - - graph_builder.py
- - - - nodes
- - - - - <reply_subgraph_nodes>
- 


Next step: add vector db and RAG layer with local fs structure, add specific node to read it