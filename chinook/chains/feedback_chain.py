import time
from typing import Dict, Any

class FeedbackChain:
    def __init__(self, running_log):
        self.running_log = running_log
    
    def log_execution(self, 
                     original_question: str,
                     clarified_question: str,
                     generated_sql: str,
                     optimized_sql: str = None,
                     execution_time: float = None,
                     success: bool = True,
                     error_message: str = None,
                     result_summary: str = None,
                     performance_metrics: Dict = None,
                     natural_response: str = None):
        """记录查询执行的详细信息"""
        
        log_data = {
            'original_question': original_question,
            'clarified_question': clarified_question,
            'generated_sql': generated_sql,
            'optimized_sql': optimized_sql,
            'execution_time': execution_time,
            'success': success,
            'error_message': error_message,
            'result_summary': result_summary,
            'performance_metrics': performance_metrics or {},
            'natural_response': natural_response
        }
        
        self.running_log.log_attempt(log_data)