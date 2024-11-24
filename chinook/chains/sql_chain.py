from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.settings import LLM

class SQLChain:
    def __init__(self):
        self.llm = LLM
        self.prompt = ChatPromptTemplate.from_template("""
        Based on the table schema below, generate a SQL query.
        DO NOT include any explanations, ONLY return the SQL query itself.
        
        Schema: {schema}
        Question: {question}
        
        SQL Query:""")
        
        self.parser = StrOutputParser()
        
        self.chain = (
            self.prompt 
            | self.llm 
            | self.parser
        )
    
    def generate_query(self, question: str, schema: str):
        return self.chain.invoke({
            "schema": schema,
            "question": question
        })