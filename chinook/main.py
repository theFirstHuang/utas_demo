import os
import time
from typing import Dict, Any
from database.connection import get_db
# from database.models import RunningLog
from chains.intent_chain import IntentClarificationChain
# from chains.sql_chain import SQLChain
# from chains.optimization_chain import QueryOptimizationChain
# from chains.feedback_chain import FeedbackChain

class FullChain:
    def __init__(self):
        self.db = get_db()
        # self.running_log = RunningLog(self.db)
        self.intent_chain = IntentClarificationChain()
        # self.sql_chain = SQLChain()
        # self.optimization_chain = QueryOptimizationChain()
        # self.feedback_chain = FeedbackChain(self.running_log)
        
    def process_question(self, question: str) -> Dict[str, Any]:
        schema = self.db.get_table_info()
        
        """
        处理用户问题的主要流程
        1. 意图理解和澄清
        2. SQL生成
        3. 查询优化（如果需要）
        4. 执行查询
        5. 记录日志
        """
        try:
            # 1. Intent Clarification
            print('--- RUNNING Chain 1: intent_chain')
            intent_result = self.intent_chain.clarify(question, schema)
            print(intent_result)

            if not intent_result['is_clear']:
                return {
                    'status': 'needs_clarification',
                    'missing_info': intent_result['missing_info']
                }
            
        except Exception as e:
            return {
                'status': 'system_error',
                'error': str(e)
            }

if __name__ == "__main__":
    chain = FullChain()
    result = chain.process_question(
        "我想要知道最有激情的音乐中卖的最多是哪一个"
    )
    print(result)