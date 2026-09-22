from typing import TypedDict
import os

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from weather import get_weather
from policy_engine import find_matching_sops, select_best_sop
from prompts import SYSTEM_PROMPT

# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()

# Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    
)


# -----------------------------
# LangGraph State
# -----------------------------
class WeatherState(TypedDict):
    user_query: str
    city: str
    weather: dict | None
    matched_sop: dict | None
    response: str
    history: list


def resolve_city_node(state: WeatherState):
    # Reuse previous city if empty
    if state["city"].strip() == "" and state["history"]:
        state["city"] = state["history"][-1]["city"]

    # Handle follow-up questions like "what about this evening?"
    followup_words = ["evening", "tomorrow", "later", "morning", "afternoon"]

    if state["history"]:
        query = state["user_query"].lower()

        if any(word in query for word in followup_words):
            previous_query = state["history"][-1]["query"]
            state["user_query"] = previous_query + " " + state["user_query"]

    return state

# -----------------------------
# Node 1 - Fetch Weather
# -----------------------------
def fetch_weather_node(state: WeatherState):
    weather = get_weather(state["city"])
    state["weather"] = weather
    return state


# -----------------------------
# Node 2 - Match SOP
# -----------------------------
def sop_node(state: WeatherState):
    matches = find_matching_sops(
        state["user_query"],
        state["weather"]
    )

    best = select_best_sop(matches)
    state["matched_sop"] = best

    return state


# -----------------------------
# Node 3 - Generate Response
# -----------------------------
def response_node(state: WeatherState):

    sop = state["matched_sop"]
    weather = state["weather"]

    if sop is None:
        state["response"] = (
            "No weather safety policy applies to this activity under the current conditions."
        )
        return state

    prompt = f"""
User Question:
{state["user_query"]}

City: {state["city"]}

Weather:
Temperature: {weather["temperature"]}°C
Wind Speed: {weather["wind_speed"]} km/h
Rain Probability: {weather["rain_probability"]}%
Precipitation: {weather["precipitation"]} mm
UV Index: {weather["uv_index"]}

SOP:
ID: {sop["id"]}
Severity: {sop["severity"]}
Advice: {sop["advice"]}
Reason: {sop["reason"]}
"""

    try:
        answer = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])

        if isinstance(answer.content, list):
            text = ""
            for block in answer.content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text += block["text"]
                elif hasattr(block, "text"):
                    text += block.text
            state["response"] = text.strip()

        else:
            state["response"] = str(answer.content)

    except Exception:
        # Fallback if Gemini quota/API fails
        state["response"] = f"""
### Weather Summary

**Location:** {state["city"].title()}

- 🌡 Temperature: {weather["temperature"]}°C
- 💨 Wind Speed: {weather["wind_speed"]} km/h
- 🌧 Rain Probability: {weather["rain_probability"]}%
- ☀️ UV Index: {weather["uv_index"]}

### Safety Advice

{sop["advice"]}

**Reason:** {sop["reason"]}

**SOP Reference:** {sop["id"]}
"""

    return state

# -----------------------------
# Node 4 - Weather Failure
# -----------------------------
def weather_failure_node(state: WeatherState):
    state["response"] = (
        f"Unable to fetch live weather for {state['city']}. "
        "Please try again later."
    )
    return state


# -----------------------------
# Node 5 - Save Memory
# -----------------------------
def remember_node(state: WeatherState):

    state["history"].append({
        "query": state["user_query"],
        "city": state["city"],
        "sop": state["matched_sop"]["id"] if state["matched_sop"] else None
    })

    # Keep only last 10 conversations
    state["history"] = state["history"][-10:]

    return state


# -----------------------------
# Conditional Edge
# -----------------------------
def weather_check(state: WeatherState):
    if state["weather"] is None:
        return "failure"
    return "success"


# -----------------------------
# Build LangGraph Workflow
# -----------------------------
workflow = StateGraph(WeatherState)

workflow.add_node("resolve_city", resolve_city_node)
workflow.add_node("fetch_weather", fetch_weather_node)
workflow.add_node("match_sop", sop_node)
workflow.add_node("response", response_node)
workflow.add_node("remember", remember_node)
workflow.add_node("failure", weather_failure_node)

workflow.set_entry_point("resolve_city")
workflow.add_edge("resolve_city", "fetch_weather")

workflow.add_conditional_edges(
    "fetch_weather",
    weather_check,
    {
        "success": "match_sop",
        "failure": "failure"
    }
)

workflow.add_edge("match_sop", "response")
workflow.add_edge("response", "remember")
workflow.add_edge("remember", END)
workflow.add_edge("failure", END)

app_graph = workflow.compile()


# -----------------------------
# Run Graph (Testing)
# -----------------------------
if __name__ == "__main__":

    query = input("Ask your question: ")
    city = input("Enter city: ")

    result = app_graph.invoke({
        "user_query": query,
        "city": city,
        "weather": None,
        "matched_sop": None,
        "response": "",
        "history": []
    })

    print("\n===== FINAL RESPONSE =====\n")
    print(result["response"])

    print("\n===== MEMORY =====")
    print(result["history"])