import os
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
from config.settings import DB_PASSWORD, DB_NAME, DB_USER, DB_HOST, DB_PORT

def get_db():
    """Initialize database connection using SQLDatabase from langchain"""
    mysql_uri = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    return SQLDatabase.from_uri(mysql_uri)