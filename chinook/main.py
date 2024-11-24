import time
from typing import Dict, Any
from database.connection import get_db
from database.running_log_model import RunningLog
from chains.intent_chain import IntentClarificationChain
from chains.sql_chain import SQLChain
from chains.optimization_chain import QueryOptimizationChain
from chains.feedback_chain import FeedbackChain
from chains.response_chain import ResponseChain

class FullChain:
    def __init__(self):
        self.db = get_db()
        self.running_log = RunningLog(self.db)
        self.intent_chain = IntentClarificationChain()
        self.sql_chain = SQLChain()
        self.optimization_chain = QueryOptimizationChain()
        self.feedback_chain = FeedbackChain(self.running_log)
        self.response_chain = ResponseChain()
        
    def process_question(self, question: str) -> Dict[str, Any]:
        schema = self.db.get_table_info()
        
        """
        处理用户问题的主要流程
        1. 意图理解和澄清
        2. SQL生成
        3. 查询优化（如果需要）
        4. 执行查询
        5. 自然语言回复
        6. 记录日志
        """
        try:
            # 1. Intent Clarification
            print('--- RUNNING Chain 1: intent chain')
            intent_result = self.intent_chain.clarify(question, schema)
            print(intent_result)

            if not intent_result['is_clear']:
                return {
                    'status': 'needs_clarification',
                    'missing_info': intent_result['missing_info']
                }
            
            # 2. Generate SQL
            print('--- RUNNING Chain 2: sql chain')
            sql_query = self.sql_chain.generate_query(
                intent_result['clarified_question'], 
                schema
            )
            print(sql_query)

            # 3. Execute Query
            print('--- RUNNING Chain 3: query execute chain')
            start_time = time.time()
            try:
                result = self.db.run(sql_query)
                execution_time = time.time() - start_time

                # 5. generate human response
                print('Running Success')
                print('--- RUNNING Chain 5: response chain')
                if result:
                    natural_response = self.response_chain.generate_response(
                        question=question,
                        sql_query=sql_query,
                        result=result
                    )
                    print(natural_response)
                
                # 6.1 Log successful execution
                print('--- RUNNING Chain 6.1: Logging info')
                self.feedback_chain.log_execution(
                    original_question=question,
                    clarified_question=intent_result['clarified_question'],
                    generated_sql=sql_query,
                    execution_time=execution_time,
                    success=True,
                    result_summary=str(result)[:1000],
                    performance_metrics={'rows': len(result)},
                    natural_response=natural_response
                )
                
                return {
                    'status': 'success',
                    'result': result,
                    'execution_time': execution_time
                }
                
            except Exception as e:
                # 4.1 Try optimization if execution fails
                print('Running Failed')
                print('--- RUNNING Chain 4.1: query optimize chain')
                optimized_query = self.optimization_chain.optimize(
                    sql_query, 
                    str(e), 
                    schema
                )
                print(f'query after optimization:\n{optimized_query}\n')

                try:
                    # 4.2 Execute optimized query
                    print('--- RUNNING Chain 4.2: query optimize chain')
                    start_time = time.time()
                    result = self.db.run(optimized_query)
                    execution_time = time.time() - start_time

                    # 5. generate human response
                    print('Running Success after optimization')
                    print('--- RUNNING Chain 5: response chain')
                    if result:
                        natural_response = self.response_chain.generate_response(
                            question=question,
                            sql_query=sql_query,
                            result=result
                        )
                        print(natural_response)

                    print('--- RUNNING Chain 6.2: Logging info')

                    # 6.2 Log successful execution after optimized
                    self.feedback_chain.log_execution(
                        original_question=question,
                        clarified_question=intent_result['clarified_question'],
                        generated_sql=sql_query,
                        optimized_sql=optimized_query,
                        execution_time=execution_time,
                        success=True,
                        result_summary=str(result)[:1000],
                        performance_metrics={'rows': len(result)},
                        natural_response=natural_response
                    )
                    
                    return {
                        'status': 'success_after_optimization',
                        'result': result,
                        'execution_time': execution_time
                    }
                    
                except Exception as e:
                    # 5. generate human response
                    print('Running Failed after optimization')
                    print('--- RUNNING Chain 5: response chain')
                    result = "failed to run query"
                    natural_response = self.response_chain.generate_response(
                        question=question,
                        sql_query=sql_query,
                        result=result
                    )
                    print(natural_response)

                    # 6.3 Log unsuccessful execution
                    print('--- RUNNING Chain 6.3: Logging info')
                    self.feedback_chain.log_execution(
                        original_question=question,
                        clarified_question=intent_result['clarified_question'],
                        generated_sql=sql_query,
                        optimized_sql=optimized_query,
                        success=False,
                        error_message=str(e),
                        natural_response=natural_response
                    )
                    print('Full Chain finished')
                    return {
                        'status': 'error',
                        'error': str(e)
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