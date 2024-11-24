from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from config.settings import LLM

class IntentClarificationChain:
    def __init__(self):
        self.llm = LLM
        self.prompt = ChatPromptTemplate.from_template("""
        Based on the table schema below, clarify the intent of the user's question.
        
        Schema: {schema}
        Question: {question}
        
        Return a JSON with:
        1. is_clear: whether the question is clear enough to generate clarified_question for SQL
        2. missing_info: if can not generate clarified_question, list of any missing information
        3. clarified_question: the question rewritten related to schema in a clear way
        """)
        
        self.parser = JsonOutputParser()
        
        # 构建chain
        self.chain = (
            self.prompt 
            | self.llm 
            | self.parser
        )
    
    def clarify(self, question: str, schema: str):
        """使用chain处理用户问题"""
        return self.chain.invoke({
            "schema": schema,
            "question": question
        })