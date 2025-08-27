import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# OpenAI / Azure Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Provider and model
PROVIDER = "openai" if OPENAI_API_KEY else "azure"
MODEL = "gpt-3.5turbo"  
