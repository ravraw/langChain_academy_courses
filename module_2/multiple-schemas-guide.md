# LangGraph Multiple Schemas - Production Guide

## Overview

This guide covers **multiple schema patterns** in LangGraph - a powerful technique for building production-grade agents with controlled state management, private internal state, and clean input/output interfaces.

## Core Concepts

### Single Schema Limitation
By default, LangGraph uses a **single schema** for:
- Graph input
- Graph output  
- All internal node communication

This approach has limitations:
- ❌ Internal working data clutters the public interface
- ❌ No separation between private and public state
- ❌ Input/output schemas are identical (no filtering)
- ❌ Difficult to maintain clean APIs in complex workflows

### Multiple Schema Solution
Multiple schemas enable:
- ✅ **Private state** for internal node communication
- ✅ **Clean input/output interfaces** with filtered data
- ✅ **Separation of concerns** between internal logic and public API
- ✅ **Type safety** across different node interactions

## Pattern 1: Private State

### Use Case
Pass sensitive or temporary data between nodes without exposing it in the graph's input/output.

### Implementation
```python
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# Public schema - exposed to users
class OverallState(TypedDict):
    foo: int

# Private schema - internal use only
class PrivateState(TypedDict):
    baz: int  # Sensitive calculation, temporary data, etc.

def node_1(state: OverallState) -> PrivateState:
    """Convert public state to private working data"""
    return {"baz": state['foo'] + 1}

def node_2(state: PrivateState) -> OverallState:
    """Process private data and return to public schema"""
    return {"foo": state['baz'] + 1}

# Graph uses OverallState as primary schema
builder = StateGraph(OverallState)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_2", END)

graph = builder.compile()

# Input/Output only contains OverallState keys
result = graph.invoke({"foo": 1})  # Returns: {"foo": 3}
# "baz" is hidden from external interface
```

### Key Benefits
- **Data Privacy**: Sensitive calculations stay internal
- **Clean Interfaces**: Users only see relevant data
- **Modularity**: Different processing stages can use optimal schemas

## Pattern 2: Input/Output Schema Filtering

### Use Case
Control exactly what data enters and exits your graph, even when internal processing requires more complex state.

### Implementation
```python
# User-facing input schema
class InputState(TypedDict):
    question: str

# User-facing output schema  
class OutputState(TypedDict):
    answer: str

# Internal working schema (contains everything)
class OverallState(TypedDict):
    question: str
    answer: str
    notes: str          # Internal notes
    processing_time: float  # Performance metrics
    debug_info: dict    # Debugging data

def thinking_node(state: InputState):
    """Initial processing with input filtering"""
    return {
        "answer": "Processing...", 
        "notes": "User asked about " + state['question'],
        "processing_time": 0.1
    }

def answer_node(state: OverallState) -> OutputState:
    """Final processing with output filtering"""
    return {"answer": f"Final answer based on: {state['notes']}"}

# Define graph with explicit input/output schemas
graph = StateGraph(
    OverallState,                    # Internal schema
    input_schema=InputState,         # What users can pass in
    output_schema=OutputState        # What users get back
)

graph.add_node("thinking_node", thinking_node)
graph.add_node("answer_node", answer_node)
graph.add_edge(START, "thinking_node")
graph.add_edge("thinking_node", "answer_node")
graph.add_edge("answer_node", END)

compiled_graph = graph.compile()

# Clean input/output interface
result = compiled_graph.invoke({"question": "What is AI?"})
# Returns only: {"answer": "Final answer based on: User asked about What is AI?"}
# Internal state (notes, processing_time, debug_info) is filtered out
```

## Production Use Cases

### 1. API Gateway Pattern
```python
class APIInput(TypedDict):
    user_id: str
    query: str

class APIOutput(TypedDict):
    response: str
    status: str

class InternalState(TypedDict):
    user_id: str
    query: str
    response: str
    status: str
    auth_token: str      # Private
    rate_limit_info: dict  # Private
    audit_log: list      # Private

# Graph processes with full internal state
# But only exposes clean API interface
```

### 2. Multi-Agent Coordination
```python
class AgentInput(TypedDict):
    task: str

class AgentOutput(TypedDict):
    result: str

class CoordinationState(TypedDict):
    task: str
    result: str
    agent_assignments: dict  # Which agent handles what
    communication_log: list  # Inter-agent messages
    resource_allocation: dict  # Private resource management

# Each agent gets clean input, coordination happens privately
```

### 3. Data Processing Pipeline
```python
class PipelineInput(TypedDict):
    raw_data: str

class PipelineOutput(TypedDict):
    processed_data: str
    confidence: float

class ProcessingState(TypedDict):
    raw_data: str
    processed_data: str
    confidence: float
    intermediate_results: list  # Private processing steps
    error_logs: list           # Private error tracking
    performance_metrics: dict  # Private monitoring data
```

## Advanced Patterns

### Mixed Schema Nodes
```python
def hybrid_node(state: OverallState) -> PrivateState:
    """Node that reads from overall state but outputs private state"""
    return {"sensitive_calculation": process_sensitive_data(state)}

def aggregator_node(state: PrivateState) -> OverallState:
    """Node that reads private state but outputs to overall state"""
    return {"public_result": aggregate_private_results(state)}
```

### Schema Transformation Chains
```python
# Chain of schema transformations
UserInput -> InternalProcessing -> PrivateCalculation -> PublicResult -> UserOutput

def input_transformer(state: UserInput) -> InternalProcessing:
    """Transform user input to internal format"""
    pass

def private_processor(state: InternalProcessing) -> PrivateCalculation:
    """Handle sensitive processing"""
    pass

def result_aggregator(state: PrivateCalculation) -> PublicResult:
    """Prepare results for output"""
    pass

def output_formatter(state: PublicResult) -> UserOutput:
    """Format final user-facing output"""
    pass
```

## Best Practices for Production

### 1. Schema Design Principles
```python
# ✅ Good: Clear separation of concerns
class UserFacingInput(TypedDict):
    query: str
    user_preferences: dict

class InternalState(TypedDict):
    query: str
    user_preferences: dict
    system_context: dict     # Internal only
    processing_metadata: dict  # Internal only

class UserFacingOutput(TypedDict):
    response: str
    suggestions: list

# ❌ Bad: Mixing concerns
class MixedState(TypedDict):
    query: str               # User data
    internal_tokens: str     # Should be private
    response: str            # User data
    debug_trace: list        # Should be private
```

### 2. Type Safety Guidelines
```python
from typing import Union, Optional

def type_safe_node(state: InputState) -> Union[OutputState, PrivateState]:
    """Use union types when node can return multiple schemas"""
    if condition:
        return OutputState({"result": "success"})
    else:
        return PrivateState({"internal_error": "details"})

def optional_state_node(state: Optional[PrivateState]) -> OverallState:
    """Handle cases where private state might be None"""
    if state is None:
        return {"error": "No private state available"}
    return {"result": process_private_state(state)}
```

### 3. Error Handling
```python
class ErrorState(TypedDict):
    error_type: str
    error_message: str
    stack_trace: str     # Private debugging info

def error_handling_node(state: OverallState) -> Union[OverallState, ErrorState]:
    """Handle errors with appropriate schema"""
    try:
        result = risky_operation(state)
        return {"success_result": result}
    except Exception as e:
        # Return error state for internal handling
        return ErrorState({
            "error_type": type(e).__name__,
            "error_message": str(e),
            "stack_trace": traceback.format_exc()
        })
```

### 4. Testing Strategies
```python
def test_schema_filtering():
    """Test that schemas properly filter input/output"""
    # Test input filtering
    result = graph.invoke({
        "valid_input": "test",
        "invalid_input": "should_be_filtered"  # Should be ignored
    })
    
    # Test output filtering
    assert "internal_data" not in result
    assert "public_result" in result

def test_private_state_isolation():
    """Test that private state doesn't leak"""
    # Private state should not appear in final output
    result = graph.invoke({"input": "test"})
    assert "private_calculation" not in result
```

## Performance Considerations

### 1. Memory Management
```python
class OptimizedState(TypedDict):
    # Keep private state minimal to reduce memory usage
    large_dataset: Optional[bytes]  # Only load when needed
    processed_summary: str          # Keep lightweight results

def memory_efficient_node(state: OptimizedState):
    """Process large data without keeping it in state"""
    if state.get("large_dataset"):
        # Process and immediately discard large data
        summary = process_large_dataset(state["large_dataset"])
        return {"processed_summary": summary, "large_dataset": None}
```

### 2. Schema Validation Overhead
```python
from pydantic import BaseModel

# For production, consider Pydantic for validation
class ValidatedInput(BaseModel):
    query: str
    user_id: str
    
    class Config:
        # Optimize for performance
        validate_assignment = False
        arbitrary_types_allowed = True
```

## Security Considerations

### 1. Sensitive Data Isolation
```python
class SecureState(TypedDict):
    # Public data
    user_request: str
    public_response: str

class PrivateSecurityState(TypedDict):
    # Sensitive data - never exposed
    auth_tokens: dict
    user_pii: dict
    system_secrets: dict

# Ensure sensitive data never leaks to output schemas
```

### 2. Input Sanitization
```python
def sanitize_input_node(state: RawInput) -> CleanInput:
    """Sanitize and validate input before processing"""
    return {
        "clean_query": sanitize_string(state["raw_query"]),
        "validated_params": validate_parameters(state["params"])
    }
```

## Migration Strategies

### From Single to Multiple Schemas
```python
# Phase 1: Keep existing single schema
class LegacyState(TypedDict):
    all_data: dict

# Phase 2: Introduce internal schema while maintaining compatibility
class InternalState(LegacyState):
    private_processing: dict

# Phase 3: Split into proper input/output schemas
class NewInput(TypedDict):
    user_data: dict

class NewOutput(TypedDict):
    result: dict
```

## Monitoring and Debugging

### 1. Schema Transition Logging
```python
import logging

def log_schema_transitions(func):
    """Decorator to log schema changes"""
    def wrapper(state):
        input_schema = type(state).__name__
        result = func(state)
        output_schema = type(result).__name__
        logging.info(f"Schema transition: {input_schema} -> {output_schema}")
        return result
    return wrapper

@log_schema_transitions
def tracked_node(state: InputState) -> OutputState:
    return process_state(state)
```

### 2. State Inspection Tools
```python
def debug_state_schemas(graph):
    """Development helper to inspect schema usage"""
    for node_name, node_func in graph.nodes.items():
        input_type = node_func.__annotations__.get('state', 'Unknown')
        return_type = node_func.__annotations__.get('return', 'Unknown')
        print(f"{node_name}: {input_type} -> {return_type}")
```

## Key Takeaways

1. **Use Private State** for sensitive or temporary data that shouldn't be exposed
2. **Implement Input/Output Filtering** for clean API interfaces  
3. **Separate Concerns** with appropriate schema boundaries
4. **Maintain Type Safety** with proper annotations
5. **Test Schema Isolation** to prevent data leaks
6. **Consider Performance** when designing complex schema hierarchies
7. **Plan for Security** by isolating sensitive data in private schemas

Multiple schemas are essential for building production-grade LangGraph applications that are secure, maintainable, and provide clean interfaces to users while supporting complex internal processing logic.