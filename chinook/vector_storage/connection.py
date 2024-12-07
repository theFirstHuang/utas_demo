# vector_store/connection.py
import chromadb
from chromadb.config import Settings
from typing import Optional

class ChromaDBConnection:
    """ChromaDB连接管理类"""
    _instance: Optional['ChromaDBConnection'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 本地持久化存储配置
            cls._instance.client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
        return cls._instance
    
    def get_client(self):
        return self.client
    
    def get_or_create_collection(self, name: str, metadata: Optional[dict] = None):
        # 设置默认metadata
        default_metadata = {
            "description": f"Collection for {name}",
            "type": "music_data",
            "created_at": "2024-12-07"
        }
        
        # 如果提供了metadata，则更新默认值
        if metadata:
            default_metadata.update(metadata)
            
        try:
            # 尝试获取已存在的集合
            return self.client.get_collection(name=name)
        except ValueError:
            # 如果集合不存在，创建新集合
            return self.client.create_collection(
                name=name,
                metadata=default_metadata
            )
    
    #reset DB, for testing only
    def reset(self):
        self.client.reset()
