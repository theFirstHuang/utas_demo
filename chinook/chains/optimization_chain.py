from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.settings import LLM


class QueryOptimizationChain:
    def __init__(self):
        self.llm = LLM
        self.prompt = ChatPromptTemplate.from_template("""
        Given the following SQL query and error (if any), optimize or fix the query.
        Only return the optimized SQL query, no explanations.
        
        Original Query: {query}
        Error Message: {error}
        Schema: {schema}
        
        Optimized Query:""")
        
        self.parser = StrOutputParser()
        
        self.chain = (
            self.prompt 
            | self.llm 
            | self.parser
        )
    
    def optimize(self, query: str, error: str, schema: str):
        return self.chain.invoke({
            "query": query,
            "error": error,
            "schema": schema
        })