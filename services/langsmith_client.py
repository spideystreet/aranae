import os
from langsmith import Client
from dotenv import load_dotenv

load_dotenv()

# Initialize LangSmith client
ls_client = Client()

def get_hub_handle():
    return os.getenv("LANGSMITH_HUB_HANDLE", "-")

def pull_hub_prompt(prompt_name: str):
    """Fetch a prompt from LangChain Hub using the configured handle."""
    handle = get_hub_handle()
    prompt_id = f"{handle}/{prompt_name}" if handle else prompt_name
    print(f"--- Pulling prompt from Hub: {prompt_id} ---")
    return ls_client.pull_prompt(prompt_id)
