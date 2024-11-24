from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

class IntentClarificationChain:
    def __init__(self):
        self.llm = ChatOpenAI()
        self.prompt = ChatPromptTemplate.from_template("""
        Based on the table schema below, clarify the intent of the user's question.
        
        Schema: {schema}
        Question: {question}
        
        Please analyze:
        1. Is the question specific and clear enough for a SQL query?
        2. Are there any ambiguous terms or missing information?
        3. What assumptions should be made about the request?
        
        Return a JSON with this format:
        {
            "is_clear": true/false,
            "missing_info": ["list of missing information"],
            "clarified_question": "rewritten clear question"
        }
        """)
    
    async def clarify(self, question: str, schema: str) -> dict:
        response = await self.llm.ainvoke(
            self.prompt.format(
                schema=schema,
                question=question
            )
        )
        return response.content