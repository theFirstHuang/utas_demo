import os
import time
from typing import Dict, Any
from database.connection import get_db
from database.models import RunningLog
from chains.intent_chain import IntentClarificationChain
from chains.sql_chain import SQLChain
from chains.optimization_chain import QueryOptimizationChain
from chains.feedback_chain import FeedbackChain

class FullChain:
    def __init__(self):
        self.db = get_db()
        self.running_log = RunningLog(self.db)
        self.intent_chain = IntentClarificationChain()
        self.sql_chain = SQLChain()
        self.optimization_chain = QueryOptimizationChain()
        self.feedback_chain = FeedbackChain(self.running_log)
        
    async def process_question(self, question: str) -> Dict[str, Any]:
        """
        处理用户问题的主要流程
        1. 意图理解和澄清
        2. SQL生成
        3. 查询优化（如果需要）
        4. 执行查询
        5. 记录日志
        """
        try:
            # 待实现: 调用各个chain处理问题
            pass
            
        except Exception as e:
            return {
                'status': 'system_error',
                'error': str(e)
            }

if __name__ == "__main__":
    import asyncio
    
    async def main():
        chain = FullChain()
        result = await chain.process_question(
            "Show me all rock music sales from last month"
        )
        print(result)

    asyncio.run(main())