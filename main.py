import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import Annotated, Optional, List
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def a1(state: State) -> State:
    print("a1")
    return state


def a2(state: State) -> State:
    print("a2")
    return state


builder = StateGraph(State)

builder.add_node("a1", a1)
builder.add_node("a2", a2)

builder.set_entry_point("a1")
builder.add_edge("a1", "a2")
builder.add_edge("a2", END)

graph = builder.compile(checkpointer=MemorySaver())
graph.get_graph().draw_mermaid_png(output_file_path="main-flow.png")

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "test-thread"}}
    print("START!")

    while True:
        user_input = input("\n> ")
        initial_state = {"messages": [HumanMessage(content=user_input)]}
        for event in graph.stream(initial_state, config=config):
            print(event)
            print("--------------------------------")
