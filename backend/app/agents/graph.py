from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.response import generate_response
from app.agents.retrieval import retrieve_context
from app.agents.router import route_query
from app.agents.state import AgentState
from app.agents.verification import verify_answer
from app.agents.web_search import search_web
from app.core.config import get_settings


async def run_agent_graph(initial_state: AgentState, db: AsyncSession) -> AgentState:
    # Kept as explicit async orchestration so database/session dependencies remain simple.
    # LangGraph is used for the production graph shape and can be visualized or extended.
    try:
        from langgraph.graph import END, StateGraph

        graph = StateGraph(AgentState)
        graph.add_node("router", route_query)
        graph.add_node("retrieval", lambda state: retrieve_context(state, db))
        graph.add_node("web_search", search_web)
        graph.add_node("response", generate_response)
        graph.add_node("verification", verify_answer)
        graph.set_entry_point("router")
        graph.add_edge("router", "retrieval")
        graph.add_edge("retrieval", "web_search")
        graph.add_edge("web_search", "response")
        graph.add_edge("response", "verification")
        graph.add_edge("verification", END)
        compiled = graph.compile()
        state = await compiled.ainvoke(initial_state)
    except Exception:
        state = await _run_linear_graph(initial_state, db)

    settings = get_settings()
    while state.get("needs_retry") and state.get("reflection_cycles", 0) < settings.max_reflection_cycles:
        state["reflection_cycles"] = state.get("reflection_cycles", 0) + 1
        state["query"] = f"{initial_state['query']}\nFocus on missing evidence and citation support."
        state = await _run_linear_graph(state, db)

    return state


async def _run_linear_graph(initial_state: AgentState, db: AsyncSession) -> AgentState:
    state = route_query(initial_state)
    state = await retrieve_context(state, db)
    state = await search_web(state)
    state = await generate_response(state)
    return verify_answer(state)
