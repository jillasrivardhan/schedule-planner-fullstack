from typing import TypedDict, Annotated
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from .config import OLLAMA_MODEL, OLLAMA_BASE_URL
from .tools import get_tasks_tool, get_preferences_tool, get_calendar_tool

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    target_date: str
    planning_context: str
    priority_order: list[str]

SYSTEM_PROMPT = """
You are the reasoning layer of an AI daily schedule planner.

Do NOT calculate exact clock times. Python handles exact time arithmetic.

You must:
1. Use the task, preference and calendar tools before deciding priorities.
2. Understand the user's request.
3. Decide which pending tasks deserve attention first.
4. Never invent tasks.
5. Never move or modify fixed calendar events.
6. Return a concise priority list using the exact task titles when finished.
"""

llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0)
tools = [get_tasks_tool, get_preferences_tool, get_calendar_tool]
llm_with_tools = llm.bind_tools(tools)

def agent_node(state: AgentState):
    response = llm_with_tools.invoke([SystemMessage(content=SYSTEM_PROMPT)] + state["messages"])
    return {"messages": [response]}

def route_tools(state: AgentState):
    return "tools" if getattr(state["messages"][-1], "tool_calls", None) else "finish"

def finish_node(state: AgentState):
    text = state["messages"][-1].content or ""
    return {"planning_context": text, "priority_order": [x.strip(" -•*0123456789.)") for x in text.splitlines() if x.strip()]}

def build_agent():
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))
    graph.add_node("finish", finish_node)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", route_tools, {"tools": "tools", "finish": "finish"})
    graph.add_edge("tools", "agent")
    graph.add_edge("finish", END)
    return graph.compile()

agent = build_agent()

def run_agent(target_date: str, user_request: str):
    result = agent.invoke({
        "messages": [HumanMessage(content=f"Target date: {target_date}\nUser request: {user_request}\nGather all relevant context and decide the task priority order.")],
        "target_date": target_date,
        "planning_context": "",
        "priority_order": [],
    })
    return result
