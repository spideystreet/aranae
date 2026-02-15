import json
import os
import sys
from typing import TypedDict, List
from dotenv import load_dotenv

# Load environment variables (contains LangSmith and DB config)
load_dotenv()

# Add project root to sys.path to allow importing from services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.database import fetch_latest_jobs

from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage
from langsmith import Client

# Initialize LangSmith client
ls_client = Client()

# --- State Definition ---
# ... (rest of imports)

def quality_checker(state: AgentState):
    """Analyze the data sample for inconsistencies using Qwen 2.5 via Ollama."""
    # Disable streaming to prevent hanging on local setup
    llm = ChatOllama(model="qwen2.5:7b", temperature=0, stream=False)
    
    print(f"--- [Node: Checker] Analyzing {len(state['data_sample'])} jobs ---")
    data_str = json.dumps(state['data_sample'], indent=2, ensure_ascii=False)
    
    # Pull prompt from LangChain Hub
    prompt_template = ls_client.pull_prompt("synapse-checker")
    prompt_value = prompt_template.invoke({"data_str": data_str})
    
    # Convert to string manually to ensure compatibility with local Ollama
    messages = prompt_value.to_messages()
    full_prompt_str = ""
    for msg in messages:
        if msg.type == 'system':
            full_prompt_str += f"System: {msg.content}\n\n"
        elif msg.type == 'human':
            full_prompt_str += f"Human: {msg.content}\n\n"
            
    response = llm.invoke(full_prompt_str)
    content = response.content
    
    # Simple parsing logic
    is_valid = "Status: VALID" in content
    
    return {
        "analysis": content,
        "is_valid": is_valid,
        "iterations": state.get('iterations', 0) + 1
    }

def data_fixer(state: AgentState):
    """Attempt to fix the data based on the quality analysis."""
    print("--- [Node: Fixer] Attempting to correct data patterns ---")
    llm = ChatOllama(model="qwen2.5:7b", temperature=0, stream=False)
    
    data_str = json.dumps(state['data_sample'], indent=2, ensure_ascii=False)
    
    # Pull prompt from LangChain Hub
    prompt_template = ls_client.pull_prompt("synapse-fixer")
    prompt_value = prompt_template.invoke({
        "data_str": data_str,
        "analysis": state['analysis']
    })
    
    # Convert to string manually
    messages = prompt_value.to_messages()
    full_prompt_str = ""
    for msg in messages:
        if msg.type == 'system':
            full_prompt_str += f"System: {msg.content}\n\n"
        elif msg.type == 'human':
            full_prompt_str += f"Human: {msg.content}\n\n"
            
    response = llm.invoke(full_prompt_str)
    content = response.content
    
    # Extract JSON from response
    try:
        json_str = content.split("JSON:")[1].strip()
        new_data = json.loads(json_str)
        return {"data_sample": new_data}
    except Exception as e:
        print(f"Error in fixer: {e}")
        return state

def routing_logic(state: AgentState):
    """Decide what to do next based on validity and iteration count."""
    if state['is_valid'] or state.get('iterations', 0) >= 3:
        return "reporter"
    return "fixer"

def reporting_node(state: AgentState):
    """Formate le rapport final."""
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
    
    # Conditional edge: Decision point
    workflow.add_conditional_edges(
        "checker",
        routing_logic,
        {
            "fixer": "fixer",
            "reporter": "reporter"
        }
    )
    
    workflow.add_edge("fixer", "checker") # Loop back to check again
    workflow.add_edge("reporter", END)
    
    return workflow.compile()

# --- Entry point for test ---

if __name__ == "__main__":
    # Fetch real data from the database
    print("\n--- STANDALONE AGENT EXECUTION ---")
    sample_data = fetch_latest_jobs(limit=2) # Reduced for testing
    
    if not sample_data:
        print("No data found in DB. Please run the scraper first.")
    else:
        print(f"Found {len(sample_data)} jobs. Starting analysis...")
        app = create_workflow()
        result = app.invoke({"data_sample": sample_data})
        print("\n--- ANALYSIS FINISHED ---")
