import os
from dotenv import load_dotenv, find_dotenv
from groq import Groq


_ = load_dotenv(find_dotenv()) # read local .env file

# Langchain settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Database settings
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv('DB_PASSWORD'),
    'database': 'chinook',
    'port': 3306
}

# openAI LLM settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LLM_MODEL = "gpt-3.5-turbo"

#Groq
from groq import Groq
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")



# Logging settings
LOG_LEVEL = "INFO"