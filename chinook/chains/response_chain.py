# response_chain.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.settings import LLM

class ResponseChain:
    def __init__(self):
        self.llm = LLM
        self.prompt = ChatPromptTemplate.from_template("""
        Based on the following SQL query result, please provide a natural language response to the original question.
        Try to be concise but informative, and make the response sound natural.
        
        Original Question: {question}
        SQL Query: {sql_query}
        Query Result: {result}
        
        Natural Language Response:""")
        
        self.parser = StrOutputParser()
        
        self.chain = (
            self.prompt 
            | self.llm 
            | self.parser
        )
    
    def generate_response(self, question: str, sql_query: str, result: Any) -> str:
        return self.chain.invoke({
            "question": question,
            "sql_query": sql_query,
            "result": result
        })