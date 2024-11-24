import os
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq


_ = load_dotenv(find_dotenv()) # read local .env file

# Database settings
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = 'chinook'
DB_USER = 'root'
DB_HOST = 'localhost'
DB_PORT = 3306


# openAI LLM settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_LLM = ChatGroq(
    model="gpt-3.5-turbo",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

#Groq
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_LLM = ChatGroq(
    model="llama3-8b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Set the currently using LLM here
LLM = GROQ_LLM