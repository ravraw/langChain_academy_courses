import random
from langgraph.graph import StateGraph, START, END
from typing import Literal, TypedDict

# define state
class State(TypedDict):
    prompt: str
    mood: str
    answer: str


#define nodes
def node_1(state: State):
    print("---Node 1---")
    return {"answer": state["prompt"] + "i'am feeling "}

def node_2(state: State):
    print("---Node 2---")
    mood = "happy"
    answer = state["prompt"] + "i'am feeling " + mood
    return {"mood": mood, "answer": answer}


def node_3(state: State):
    print("---Node 3---")
    mood = "sad"
    answer = state["prompt"] + "i'am feeling " + mood
    return {"mood": mood, "answer": answer}

def get_mood(state: State) -> Literal["node_2", "node_3"]:
    return random.choice(["node_2", "node_3"])

#build graph
builder = StateGraph(State)

builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", get_mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)


graph = builder.compile()

result = graph.invoke({"prompt": "What is your mood?"})
print(result["answer"])
