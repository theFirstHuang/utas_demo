import os
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv

load_dotenv()

def get_db():
    """Get database connection"""
    mysql_uri = f'mysql+mysqlconnector://root:{os.getenv("DB_PASSWORD")}@localhost:3306/chinook'
    return SQLDatabase.from_uri(mysql_uri)