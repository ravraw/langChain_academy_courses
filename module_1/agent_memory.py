from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
import sqlite3

# Load environment variables
load_dotenv()

# Define tools for the agent
def get_weather(location: str) -> str:
    """Get the current weather for a location.

    Args:
        location: The city/location to get weather for
    """
    # Simulate weather API call
    weather_data = {
        "New York": "Sunny, 72°F",
        "London": "Cloudy, 60°F", 
        "Tokyo": "Rainy, 65°F",
        "San Francisco": "Foggy, 58°F"
    }
    return weather_data.get(location, f"Weather data not available for {location}")

def calculate(expression: str) -> str:
    """Safely calculate a mathematical expression.

    Args:
        expression: Mathematical expression to calculate (e.g., "2 + 3 * 4")
    """
    try:
        # Simple safe evaluation for basic math
        allowed_chars = set("0123456789+-*/.() ")
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return f"Result: {result}"
        else:
            return "Error: Invalid characters in expression"
    except Exception as e:
        return f"Error calculating: {str(e)}"

def remember_fact(fact: str) -> str:
    """Remember an important fact for later reference.

    Args:
        fact: Important information to remember
    """
    # This is handled by the memory system, but we acknowledge the storage
    return f"I'll remember that: {fact}"

# Available tools
tools = [get_weather, calculate, remember_fact]

# Define LLM with bound tools
llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
llm_with_tools = llm.bind_tools(tools)

# System message with memory instructions
sys_msg = SystemMessage(content="""You are a helpful assistant with memory capabilities. 
You can:
1. Get weather information for cities
2. Perform mathematical calculations  
3. Remember important facts from our conversation

Key behaviors:
- Remember important details from our conversation across multiple interactions
- Reference previous conversations when relevant
- If asked about something from earlier, check your memory
- Be conversational and helpful
- Use tools when appropriate to provide accurate information
""")

# Agent node that uses LLM with tools
def agent_node(state: MessagesState):
    """Main agent node that processes messages and calls tools if needed."""
    messages = [sys_msg] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# Memory setup with SQLite checkpointing
def setup_memory():
    """Initialize SQLite-based memory system."""
    # Create in-memory SQLite database for this session
    # In production, you might want to use a persistent file
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    return SqliteSaver(conn)

# Build the graph with memory
def create_agent_with_memory():
    """Create and compile the agent graph with memory capabilities."""
    
    # Initialize memory
    memory = setup_memory()
    
    # Build graph
    builder = StateGraph(MessagesState)
    
    # Add nodes
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(tools))
    
    # Add edges
    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent",
        tools_condition,  # Routes to tools if tool calls present, END otherwise
    )
    builder.add_edge("tools", "agent")  # After tools, go back to agent
    
    # Compile with memory
    agent_with_memory = builder.compile(checkpointer=memory)
    
    return agent_with_memory

# Create the agent
agent_graph = create_agent_with_memory()

# Helper function to run conversations with memory
def chat_with_memory(message: str, thread_id: str = "default_conversation"):
    """
    Chat with the agent, maintaining conversation history.
    
    Args:
        message: User's message
        thread_id: Unique identifier for the conversation thread
    """
    # Configuration for this conversation thread
    config = {"configurable": {"thread_id": thread_id}}
    
    # Create user message
    user_message = HumanMessage(content=message)
    
    # Invoke agent with memory
    result = agent_graph.invoke(
        {"messages": [user_message]}, 
        config=config
    )
    
    # Return the last AI message
    return result["messages"][-1].content

# Demo function to test the agent
def demo_agent():
    """Demonstrate the agent's memory capabilities."""
    print("=== LangGraph Agent with Memory Demo ===\n")
    
    # Conversation 1
    print("User: Hi, my name is Alice and I live in New York")
    response1 = chat_with_memory("Hi, my name is Alice and I live in New York")
    print(f"Agent: {response1}\n")
    
    # Conversation 2 - Agent should remember the name
    print("User: What's the weather like where I live?")
    response2 = chat_with_memory("What's the weather like where I live?")
    print(f"Agent: {response2}\n")
    
    # Conversation 3 - Test calculation
    print("User: Can you calculate 15 * 24 + 100?")
    response3 = chat_with_memory("Can you calculate 15 * 24 + 100?")
    print(f"Agent: {response3}\n")
    
    # Conversation 4 - Remember a fact
    print("User: Please remember that my favorite color is blue")
    response4 = chat_with_memory("Please remember that my favorite color is blue")
    print(f"Agent: {response4}\n")
    
    # Conversation 5 - Test memory recall
    print("User: What's my name and favorite color?")
    response5 = chat_with_memory("What's my name and favorite color?")
    print(f"Agent: {response5}\n")

if __name__ == "__main__":
    # Run the demo
    demo_agent()
    
    # Interactive mode
    print("\n=== Interactive Mode ===")
    print("Type 'quit' to exit")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            break
            
        try:
            response = chat_with_memory(user_input)
            print(f"Agent: {response}")
        except Exception as e:
            print(f"Error: {e}")
