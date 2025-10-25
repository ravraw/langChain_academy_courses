# LangGraph State Reducers - Complete Guide

## Overview

This document explains **LangGraph State Reducers** - a fundamental concept for managing state updates in LangGraph workflows, especially when multiple nodes run in parallel and attempt to modify the same state keys.

## The Core Problem: State Conflicts

### Default Behavior Issue
By default, LangGraph simply **overwrites** state values when nodes return updates. This creates problems when:

1. Multiple nodes run in parallel (same execution step)
2. Both nodes try to update the same state key
3. LangGraph doesn't know which update to keep

**Example of the Problem:**
```python
class State(TypedDict):
    foo: int

def node_2(state):
    return {"foo": state['foo'] + 1}  # Returns foo = 2

def node_3(state):
    return {"foo": state['foo'] + 1}  # Also returns foo = 2

# When both run in parallel -> InvalidUpdateError!
```

## Solution: State Reducers

**Reducers** are functions that specify HOW to combine state updates from multiple sources, rather than just overwriting.

### Basic Syntax
```python
from typing import Annotated

class State(TypedDict):
    key_name: Annotated[data_type, reducer_function]
```

## Built-in Reducers

### 1. `operator.add` - List Concatenation
```python
from operator import add
from typing import Annotated

class State(TypedDict):
    foo: Annotated[list[int], add]  # Concatenates lists

def node_1(state):
    return {"foo": [1]}  # Returns [1]

def node_2(state):
    return {"foo": [2]}  # Returns [2]

# Result: foo = [1, 2] (concatenated, not overwritten)
```

### 2. `add_messages` - Message Management
```python
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
```

## Custom Reducers

### Creating Safe List Combiners
```python
def reduce_list(left: list | None, right: list | None) -> list:
    """Safely combine two lists, handling None values.
    
    Args:
        left: First list (or None)
        right: Second list (or None)
        
    Returns:
        Combined list with all elements
    """
    if not left:
        left = []
    if not right:
        right = []
    return left + right

class SafeState(TypedDict):
    items: Annotated[list[int], reduce_list]
```

### Benefits of Custom Reducers
- **Null Safety**: Handle None/empty values gracefully
- **Type Safety**: Ensure proper data types
- **Business Logic**: Implement domain-specific combination rules
- **Error Prevention**: Avoid runtime crashes

## Message State Management

### MessagesState Shortcut
```python
from langgraph.graph import MessagesState

# Built-in class with messages key and add_messages reducer
class MyState(MessagesState):
    additional_field: str
    # messages key is automatically included
```

### Equivalent Manual Definition
```python
from typing import Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class CustomMessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    additional_field: str
```

## Advanced Message Operations

### 1. Message Addition
```python
# Appends new messages to existing list
initial = [AIMessage("Hello!")]
new = HumanMessage("Hi there!")
result = add_messages(initial, new)
# Result: [AIMessage("Hello!"), HumanMessage("Hi there!")]
```

### 2. Message Rewriting (Same ID)
```python
# Messages with same ID get overwritten
initial = [AIMessage("Hello!", id="1")]
updated = AIMessage("Hello there!", id="1")  # Same ID
result = add_messages(initial, updated)
# Result: [AIMessage("Hello there!", id="1")]  # Overwritten
```

### 3. Message Removal
```python
from langchain_core.messages import RemoveMessage

messages = [
    AIMessage("Hi.", id="1"),
    HumanMessage("Hello.", id="2"),
    AIMessage("How are you?", id="3")
]

# Remove specific messages by ID
delete_msgs = [RemoveMessage(id="1"), RemoveMessage(id="2")]
result = add_messages(messages, delete_msgs)
# Result: [AIMessage("How are you?", id="3")]  # Only ID 3 remains
```

## Practical Examples

### Example 1: Parallel Node Processing
```python
from operator import add
from typing import Annotated

class CounterState(TypedDict):
    values: Annotated[list[int], add]

def increment_node(state):
    last_val = state['values'][-1] if state['values'] else 0
    return {"values": [last_val + 1]}

def double_node(state):
    last_val = state['values'][-1] if state['values'] else 0
    return {"values": [last_val * 2]}

# Both nodes can run in parallel without conflicts
# Final state will have both incremented and doubled values
```

### Example 2: Agent Memory System
```python
from langgraph.graph import MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver

class AgentState(MessagesState):
    user_preferences: Annotated[dict, lambda x, y: {**x, **y}]  # Merge dicts
    conversation_context: Annotated[list[str], add]  # Accumulate context

# This allows the agent to:
# - Maintain conversation history (messages)
# - Accumulate user preferences without losing data
# - Build context over multiple interactions
```

## Best Practices

### 1. Choose Appropriate Reducers
- **Lists**: Use `add` for concatenation
- **Messages**: Use `add_messages` for conversations
- **Dictionaries**: Create custom merge functions
- **Counters**: Use custom increment/accumulate functions

### 2. Handle Edge Cases
```python
def safe_dict_merge(left: dict | None, right: dict | None) -> dict:
    """Safely merge dictionaries, handling None values."""
    if not left:
        left = {}
    if not right:
        right = {}
    return {**left, **right}
```

### 3. Type Safety
```python
from typing import Annotated, Union

class TypeSafeState(TypedDict):
    # Explicit type hints help catch errors early
    numbers: Annotated[list[int], add]
    texts: Annotated[list[str], add]
    metadata: Annotated[dict[str, Union[str, int]], safe_dict_merge]
```

## Common Use Cases

### 1. **Conversation Agents**
- Use `MessagesState` with `add_messages`
- Maintain conversation history across multiple turns
- Support message editing and deletion

### 2. **Data Aggregation**
- Collect results from multiple parallel processing nodes
- Combine lists, sets, or custom data structures
- Avoid data loss from overwrites

### 3. **Multi-Agent Systems**
- Merge outputs from different specialized agents
- Maintain shared context and state
- Coordinate between agents without conflicts

### 4. **Workflow Orchestration**
- Accumulate results from different workflow steps
- Maintain audit trails and processing history
- Handle branching and merging execution paths

## Connection to Your Project

This knowledge directly applies to your `agent_memory.py`:

```python
# Your agent uses MessagesState (built-in add_messages reducer)
class AgentState(MessagesState):
    # Automatically handles conversation history
    pass

# The SQLite checkpointer works with reducers to:
# 1. Store conversation state safely
# 2. Handle concurrent message updates
# 3. Maintain conversation context across sessions
```

## Key Takeaways

1. **Reducers prevent state conflicts** in parallel execution
2. **Built-in reducers** handle common patterns (lists, messages)
3. **Custom reducers** provide flexibility for domain-specific needs
4. **Message management** is crucial for conversational AI
5. **Type safety** and **null handling** prevent runtime errors

Understanding reducers is essential for building robust LangGraph applications with complex state management and parallel execution patterns.