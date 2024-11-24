from typing import Dict, Any
import json
import uuid
from datetime import datetime
from sqlalchemy import text

class RunningLog:
    def __init__(self, db):
        self.db = db
        
    def log_attempt(self, data: Dict[str, Any]):
        """记录一次查询尝试"""
        try:
            # 处理性能指标
            if 'performance_metrics' in data and isinstance(data['performance_metrics'], dict):
                performance_metrics = json.dumps(data.get('performance_metrics'))
            else:
                performance_metrics = None

            # 准备所有参数    
            log_id = str(uuid.uuid4())
            original_question = data.get('original_question')
            clarified_question = data.get('clarified_question')
            generated_sql = data.get('generated_sql')
            optimized_sql = data.get('optimized_sql')
            execution_time = data.get('execution_time')
            success = 1 if data.get('success') else 0
            error_message = data.get('error_message')
            result_summary = data.get('result_summary')
            natural_response = data.get('natural_response')  # 新增
            feedback_score = data.get('feedback_score')      # 新增
            feedback_comment = data.get('feedback_comment')  # 新增

            # 构建 INSERT 语句
            insert_sql = f"""
            INSERT INTO running_log (
                id, original_question, clarified_question,
                generated_sql, optimized_sql, execution_time,
                success, error_message, result_summary,
                performance_metrics, timestamp,
                natural_response, feedback_score, feedback_comment
            ) VALUES (
                '{log_id}',
                '{self._escape_string(original_question)}',
                '{self._escape_string(clarified_question)}',
                '{self._escape_string(generated_sql)}',
                '{self._escape_string(optimized_sql)}',
                {execution_time if execution_time is not None else 'NULL'},
                {success},
                '{self._escape_string(error_message)}',
                '{self._escape_string(result_summary)}',
                '{self._escape_string(performance_metrics)}',
                NOW(),
                '{self._escape_string(natural_response)}',
                {feedback_score if feedback_score is not None else 'NULL'},
                '{self._escape_string(feedback_comment)}'
            )
            """
            
            self.db.run(insert_sql)
            
        except Exception as e:
            print(f"Error logging attempt: {str(e)}")
            with open('error_log.txt', 'a') as f:
                f.write(f"\nTimestamp: {datetime.now()}\nError: {str(e)}\nData: {str(data)}\n")

    def _escape_string(self, value):
        """转义字符串中的特殊字符"""
        if value is None:
            return None
        return str(value).replace("'", "''").replace("\\", "\\\\")