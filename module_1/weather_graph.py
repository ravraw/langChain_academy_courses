import random
from langgraph.graph import StateGraph, START, END
from typing import Literal, TypedDict

# Define state for weather graph
class WeatherState(TypedDict):
    location: str
    temperature: str
    weather_condition: str
    recommendation: str

# Define nodes
def get_location(state: WeatherState):
    print("---Getting Location---")
    return {"location": state["location"]}

def check_weather(state: WeatherState):
    print("---Checking Weather---")
    # Simulate weather check
    temp = random.randint(-10, 35)
    conditions = ["sunny", "cloudy", "rainy", "snowy"]
    condition = random.choice(conditions)
    
    return {
        "temperature": f"{temp}°C",
        "weather_condition": condition
    }

def give_recommendation(state: WeatherState):
    print("---Giving Recommendation---")
    temp = int(state["temperature"].replace("°C", ""))
    condition = state["weather_condition"]
    
    if temp < 0:
        recommendation = "Bundle up! It's freezing outside. Wear warm clothes and avoid going out if possible."
    elif temp < 10:
        recommendation = "It's quite cold. Wear a jacket and warm clothes."
    elif temp < 20:
        recommendation = "Pleasant weather! Light jacket might be nice."
    elif temp < 30:
        recommendation = "Nice and warm! Perfect weather for outdoor activities."
    else:
        recommendation = "It's hot! Stay hydrated and avoid direct sun exposure."
    
    if condition == "rainy":
        recommendation += " Don't forget your umbrella!"
    elif condition == "snowy":
        recommendation += " Be careful on slippery surfaces!"
    
    return {"recommendation": recommendation}

def should_go_outside(state: WeatherState) -> Literal["stay_home", "go_outside"]:
    temp = int(state["temperature"].replace("°C", ""))
    condition = state["weather_condition"]
    
    if condition in ["rainy", "snowy"] or temp < 0:
        return "stay_home"
    else:
        return "go_outside"

def stay_home(state: WeatherState):
    print("---Staying Home---")
    return {"recommendation": state["recommendation"] + " You should stay home today."}

def go_outside(state: WeatherState):
    print("---Going Outside---")
    return {"recommendation": state["recommendation"] + " Great day to go outside!"}

# Build graph
builder = StateGraph(WeatherState)

# Add nodes
builder.add_node("get_location", get_location)
builder.add_node("check_weather", check_weather)
builder.add_node("give_recommendation", give_recommendation)
builder.add_node("stay_home", stay_home)
builder.add_node("go_outside", go_outside)

# Add edges
builder.add_edge(START, "get_location")
builder.add_edge("get_location", "check_weather")
builder.add_edge("check_weather", "give_recommendation")
builder.add_conditional_edges("give_recommendation", should_go_outside)
builder.add_edge("stay_home", END)
builder.add_edge("go_outside", END)

# Compile graph
weather_graph = builder.compile()

# Test the graph
if __name__ == "__main__":
    result = weather_graph.invoke({"location": "New York"})
    print(f"Weather for {result['location']}: {result['temperature']}, {result['weather_condition']}")
    print(f"Recommendation: {result['recommendation']}")
