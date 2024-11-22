import os
from dotenv import load_dotenv

load_dotenv()

# Database settings
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv('DB_PASSWORD'),
    'database': 'chinook',
    'port': 3306
}

# LLM settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LLM_MODEL = "gpt-3.5-turbo"

#Groq


# Logging settings
LOG_LEVEL = "INFO"