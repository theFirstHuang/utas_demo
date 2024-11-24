from typing import Dict, Any
import json
import uuid
from datetime import datetime

class RunningLog:
    def __init__(self, db):
        self.db = db
    
    def log_attempt(self, data: Dict[str, Any]):
        """记录一次查询尝试"""
        if 'performance_metrics' in data and isinstance(data['performance_metrics'], dict):
            data['performance_metrics'] = json.dumps(data['performance_metrics'])
            
        insert_sql = """
        INSERT INTO running_log (
            id, original_question, clarified_question, 
            generated_sql, optimized_sql, execution_time,
            success, error_message, result_summary, 
            performance_metrics
        ) VALUES (
            %(id)s, %(original_question)s, %(clarified_question)s,
            %(generated_sql)s, %(optimized_sql)s, %(execution_time)s,
            %(success)s, %(error_message)s, %(result_summary)s,
            %(performance_metrics)s
        )
        """
        
        data['id'] = str(uuid.uuid4())
        self.db.run(insert_sql, data)