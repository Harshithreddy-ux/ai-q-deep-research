import os
from dotenv import load_dotenv

load_dotenv()

# Read API keys from environment (or .env)
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def apply_env():
    if NVIDIA_API_KEY:
        os.environ["NVIDIA_API_KEY"] = NVIDIA_API_KEY
    if TAVILY_API_KEY:
        os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

def missing_keys():
    missing = []
    if not NVIDIA_API_KEY:
        missing.append("NVIDIA_API_KEY")
    if not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")
    return missing
