# LangGraph Academy - AI Agent Coding Instructions

This repository is a **LangGraph-based AI Agent learning project** from LangChain Academy, focusing on building state-driven graph workflows with OpenAI integration.

## Architecture Overview

**Core Pattern**: LangGraph uses `StateGraph` with typed state dictionaries (`TypedDict`) where nodes return partial state updates that get merged automatically. All graphs follow the pattern: define state → create nodes → add edges → compile.

**Graph Registration**: The `langgraph.json` config maps graph names to their module exports:

- `simple_graph`: Basic conditional routing example
- `weather_graph`: Multi-step decision workflow
- `router_graph`: Tool-calling with conditional edges
- `agent_graph`: Full agent with tools and message state

## Key Development Patterns

### State Management

```python
class State(TypedDict):
    prompt: str
    answer: str

def node_function(state: State):
    # Return only changed fields - LangGraph merges automatically
    return {"answer": state["prompt"] + " processed"}
```

### Graph Construction

1. **StateGraph**: Define with state type (`StateGraph(State)`)
2. **Nodes**: Functions that take state, return partial state updates
3. **Edges**: Use `START`/`END` constants, conditional edges for routing
4. **Compilation**: Always call `.compile()` before use

### Tool Integration

- Use `llm.bind_tools([tool_list])` for OpenAI tool binding
- `ToolNode(tools)` creates executable tool nodes
- `tools_condition` handles tool call routing automatically
- `MessagesState` is the standard state for agent conversations

## Development Workflow

### Running Graphs

```bash
# Start LangGraph Studio for visualization
uv run langgraph dev

# Run individual modules
python module_1/simple_graph.py
```

### Environment Setup

- Uses `uv` package manager (not pip/poetry)
- Requires `.env` file with `OPENAI_API_KEY`
- Python ≥3.11 required (specified in pyproject.toml)

### Project Structure

- `module_1/`: Learning modules with progressive complexity
- `langgraph.json`: Graph configuration for LangGraph Studio
- Individual graph files export their compiled graph as module-level variable

## Key Conventions

**Node Functions**: Always return dictionary with only changed state fields
**Conditional Edges**: Return literal strings matching target node names
**Tool Functions**: Include proper docstrings for OpenAI function calling
**State Updates**: LangGraph automatically merges returned dictionaries into state

## Integration Points

- **OpenAI**: Primary LLM provider via `langchain-openai`
- **LangSmith**: Observability (configured via environment)
- **LangGraph Studio**: Visual debugging (access via `uv run langgraph dev`)
- **SQLite**: Checkpointing support (langgraph-checkpoint-sqlite)

## Common Debugging

**Graph Visualization**: Use LangGraph Studio to see execution flow
**State Inspection**: Add print statements in nodes to trace state changes
**Tool Calls**: Check `tool_calls` attribute on AI messages for debugging
**Conditional Logic**: Verify conditional edge functions return exact node names

This is a learning-focused codebase - prioritize clarity and educational value over production optimizations.
