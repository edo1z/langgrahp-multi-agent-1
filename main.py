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
from langgraph.types import interrupt, Command

load_dotenv()


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    number: int


def a1(state: State, config) -> State:
    print("a1", config["metadata"])
    return {"number": 1}


def a2(state: State, config) -> State:
    print("a2", config["metadata"])

    for event in graph2.stream(state, config=config):
        print(event)
        print("--------------------------------")
        if isinstance(event, dict) and "__interrupt__" in event:
            print("[grahp2] interrupt!")

    return {"number": 2}


def b1(state: State, config) -> State:
    print("b1", config["metadata"])
    return {"number": 3}


def b2(state: State, config) -> State:
    print("b2", config["metadata"])
    number = interrupt("hello")
    print(number)
    return {"number": number}


builder = StateGraph(State)

builder.add_node("a1", a1)
builder.add_node("a2", a2)

builder.set_entry_point("a1")
builder.add_edge("a1", "a2")
builder.add_edge("a2", END)

graph = builder.compile(checkpointer=MemorySaver())
graph.get_graph().draw_mermaid_png(output_file_path="main-flow.png")

builder2 = StateGraph(State)

builder2.add_node("b1", b1)
builder2.add_node("b2", b2)

builder2.set_entry_point("b1")
builder2.add_edge("b1", "b2")
builder2.add_edge("b2", END)

graph2 = builder2.compile()
graph2.get_graph().draw_mermaid_png(output_file_path="main-flow2.png")

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "test-thread"}}
    print("START!")
    interrupted = False

    while True:
        user_input = input("\n> ")

        state = (
            Command(resume=user_input)
            if interrupted
            else {"messages": [HumanMessage(content=user_input)]}
        )

        for event in graph.stream(state, config=config):
            print(event)
            print("--------------------------------")
            if isinstance(event, dict) and "__interrupt__" in event:
                print("[grahp1] interrupt!")
                interrupted = True
            else:
                interrupted = False
