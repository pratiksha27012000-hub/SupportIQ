
import os
from pathlib import Path
from dotenv import load_dotenv

# Locate the SupportIQ project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Read Groq API key
api_key = os.getenv("GROQ_API_KEY")

if api_key:
    print("Groq API key: CONFIGURED")
else:
    print("Groq API key: NOT FOUND")
