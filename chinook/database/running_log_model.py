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
            #处理performance_metrics
            if 'performance_metrics' in data and isinstance(data['performance_metrics'], dict):
                performance_metrics = json.dumps(data.get('performance_metrics'))
            else:
                performance_metrics = None

            # 数据准备
            log_id = str(uuid.uuid4())
            original_question = data.get('original_question')
            clarified_question = data.get('clarified_question')
            generated_sql = data.get('generated_sql')
            optimized_sql = data.get('optimized_sql')
            execution_time = data.get('execution_time')
            success = 1 if data.get('success') else 0  # 转换为 TINYINT
            error_message = data.get('error_message')
            result_summary = data.get('result_summary')
            natural_response = data.get('natural_response')

            # 构建query
            insert_sql = f"""
            INSERT INTO running_log (
                id, original_question, clarified_question,
                generated_sql, optimized_sql, execution_time,
                success, error_message, result_summary,
                performance_metrics, timestamp
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
                '{self._escape_string(natural_response)}'
            )
            """
            
            print(f"Insert SQL is:\n{insert_sql}")
            self.db.run(insert_sql)
            
        except Exception as e:
            print(f"Error logging attempt: {str(e)}")
            # 记录错误到文件
            with open('error_log.txt', 'a') as f:
                f.write(f"\nTimestamp: {datetime.now()}\nError: {str(e)}\nData: {str(data)}\n")

    def _escape_string(self, value):
        """转义字符串中的特殊字符"""
        if value is None:
            return None
        # 转义单引号和其他特殊字符
        return str(value).replace("'", "''").replace("\\", "\\\\")