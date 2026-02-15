import json
import os
import sys
import re
from typing import TypedDict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to sys.path to allow importing from services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.database import fetch_latest_jobs
from services.langsmith_client import pull_hub_prompt

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

# Configuration
AGENT_MODEL = os.getenv("AGENT_MODEL", "mistralai/mistral-small-24b-instruct-2501")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def extract_json(text: str) -> dict:
    """Extracts the first JSON object or array found in text."""
    try:
        # 1. Try to find content between ```json and ``` (handles objects AND arrays)
        match = re.search(r"```(?:json)?\s*([\{\[].*?[\]\}])\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
            
        # 2. Fallback: find first { to last } OR first [ to last ]
        match = re.search(r"([\{\[].*[\]\}])", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
            
        # 3. Last resort: try whole text
        return json.loads(text)
    except Exception:
        return {}

def format_prompt_as_string(prompt_value) -> str:
    """Converts ChatPromptValue to a flat string for Ollama compatibility."""
    messages = prompt_value.to_messages()
    full_prompt_str = ""
    for msg in messages:
        role = "System" if msg.type == 'system' else "Human"
        full_prompt_str += f"{role}: {msg.content}\n\n"
    return full_prompt_str

# Pre-load prompts from LangChain Hub
print(f"--- Pre-loading prompts from LangChain Hub ---")
CHECKER_PROMPT = pull_hub_prompt("synapse-checker")
FIXER_PROMPT = pull_hub_prompt("synapse-fixer")
print("--- Prompts ready ---")

# --- State Definition ---
class AgentState(TypedDict):
    data_sample: List[dict]
    analysis: str
    is_valid: bool
    iterations: int

# --- Nodes ---

def quality_checker(state: AgentState):
    """Analyze the data sample for inconsistencies."""
    # Use OpenRouter via ChatOpenAI compatibility
    llm = ChatOpenAI(
        model=AGENT_MODEL,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0
    )
    
    print(f"--- [Node: Checker] Analyzing {len(state['data_sample'])} jobs ---")
    data_str = json.dumps(state['data_sample'], indent=2, ensure_ascii=False)
    
    prompt_value = CHECKER_PROMPT.invoke({"data_str": data_str})
    final_prompt = format_prompt_as_string(prompt_value)
    
    response = llm.invoke(final_prompt)
    res_json = extract_json(response.content)
    
    is_valid = res_json.get("is_valid", False)
    analysis = res_json.get("analysis", response.content)
    
    current_iter = state.get('iterations', 0) + 1
    print(f"   > Iteration: {current_iter} | Valid: {is_valid}")
    
    return {
        "analysis": analysis,
        "is_valid": is_valid,
        "iterations": current_iter
    }

def data_fixer(state: AgentState):
    """Attempt to fix the data based on the quality analysis."""
    print("--- [Node: Fixer] Attempting to correct data patterns ---")
    llm = ChatOpenAI(
        model=AGENT_MODEL,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0
    )
    
    data_str = json.dumps(state['data_sample'], indent=2, ensure_ascii=False)
    prompt_value = FIXER_PROMPT.invoke({
        "data_str": data_str,
        "analysis": state['analysis']
    })
    
    final_prompt = format_prompt_as_string(prompt_value)
    response = llm.invoke(final_prompt)
    res_json = extract_json(response.content)
    
    corrected_data = []
    if isinstance(res_json, list):
        corrected_data = res_json
    elif isinstance(res_json, dict):
        corrected_data = res_json.get("corrected_data", [])
    
    if corrected_data and isinstance(corrected_data, list) and len(corrected_data) > 0:
        print(f"   > Fixer: Successfully extracted {len(corrected_data)} corrected items.")
        return {"data_sample": corrected_data}
    
    print("   > Fixer: Failed to extract valid JSON data (returning original).")
    return state

def routing_logic(state: AgentState):
    if state['is_valid'] or state.get('iterations', 0) >= 3:
        return "reporter"
    return "fixer"

def reporting_node(state: AgentState):
    status_icon = "✅" if state['is_valid'] else "❌"
    print(f"\n=== RAPPORT QUALITÉ FINAL (Essai {state.get('iterations')}) {status_icon} ===")
    print(state['analysis'])
    if state['is_valid']:
        print("Données finales validées :", json.dumps(state['data_sample'], indent=2))
    return state

# --- Graph Construction ---

def create_workflow():
    workflow = StateGraph(AgentState)
    workflow.add_node("checker", quality_checker)
    workflow.add_node("fixer", data_fixer)
    workflow.add_node("reporter", reporting_node)
    
    workflow.set_entry_point("checker")
    workflow.add_conditional_edges("checker", routing_logic, {"fixer": "fixer", "reporter": "reporter"})
    workflow.add_edge("fixer", "checker")
    workflow.add_edge("reporter", END)
    
    return workflow.compile()

if __name__ == "__main__":
    print("\n--- STANDALONE AGENT EXECUTION ---")
    sample_data = fetch_latest_jobs(limit=1)
    
    if not sample_data:
        print("No data found in DB.")
    else:
        print(f"Found {len(sample_data)} jobs. Starting analysis...")
        app = create_workflow()
        result = app.invoke({"data_sample": sample_data})
        print("\n--- ANALYSIS FINISHED ---")
