from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Any
import json
import uuid
from vector_storage.connection import ChromaDBConnection

# helper function processing list meta value
def process_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """处理meta,将复杂类型转换为JSON字符串"""
    processed = {}
    for key, value in metadata.items():
        if isinstance(value, (list, dict)):
            processed[key] = json.dumps(value)
        else:
            processed[key] = value
    return processed

class VectorDocument:
    """向量文档基础模型"""
    def __init__(self, doc_id: str, content: str, metadata: Dict[str, Any], 
                 embedding: Optional[List[float]] = None):
        self.doc_id = doc_id
        self.content = content
        self.metadata = process_metadata(metadata)
        self.embedding = embedding

    def create(content: str, metadata: Dict[str, Any]):
        """创建新的文档实例,自动生成ID并添加基础元数据"""
        base_metadata = {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "doc_type": metadata.get("doc_type", "unknown")
        }
        processed_metadata = process_metadata(metadata)
        print(processed_metadata)
        base_metadata.update(processed_metadata)
        
        return VectorDocument(
            doc_id=str(uuid.uuid4()),
            content=content,
            metadata=base_metadata
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """将文档转换为字典格式"""
        return {
            "id": self.doc_id,
            "content": self.content,
            "metadata": json.dumps(self.metadata)
        }
    
    def from_dict(data: Dict[str, Any]):
        """从字典创建文档实例"""
        return VectorDocument(
            doc_id=data["id"],
            content=data["content"],
            metadata=(json.loads(data["metadata"]) 
                     if isinstance(data["metadata"], str) 
                     else data["metadata"]),
            embedding=data.get("embedding")
        )

class VectorStore:
    """向量存储操作接口"""
    def __init__(self, collection_name: str):
        self.conn = ChromaDBConnection()
        # 为集合提供基础元数据
        collection_metadata = {
            "name": collection_name,
            "description": f"Vector store for {collection_name}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.collection = self.conn.get_or_create_collection(
            collection_name,
            metadata=collection_metadata
        )

    def add_documents(self, documents: List[VectorDocument]):
        """添加文档到向量存储"""
        if not documents:
            return
        
        for doc in documents:
            print(doc.metadata)

        self.collection.add(
            ids=[doc.doc_id for doc in documents],
            documents=[doc.content for doc in documents],
            metadatas=[doc.metadata for doc in documents]
        )
    
    def search(self, query: str, n_results: int = 5, metadata_filter: Optional[Dict] = None) -> List[Dict]:
        """搜索相似文档"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=metadata_filter
        )
        
        return [
            {
                "id": id,
                "content": document,
                "metadata": metadata,
                "distance": distance
            }
            for id, document, metadata, distance in zip(
                results['ids'][0],
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )
        ]
    
    def delete(self, doc_ids: List[str]):
        """删除文档"""
        self.collection.delete(ids=doc_ids)
    
    def get(self, doc_id: str) -> Optional[Dict]:
        """获取单个文档"""
        result = self.collection.get(ids=[doc_id])
        if not result['ids']:
            return None
            
        return {
            "id": result['ids'][0],
            "content": result['documents'][0],
            "metadata": result['metadatas'][0]
        }
    
    def get_collection_info(self) -> Dict[str, Any]:
        """获取集合信息"""
        return {
            "name": self.collection.name,
            "metadata": self.collection.metadata,
            "count": self.collection.count()
        }
    
    @classmethod
    def list_collections(cls) -> List[Dict[str, Any]]:
        """列出所有集合及其信息"""
        conn = ChromaDBConnection()
        collections = conn.get_client().list_collections()
        return [{
            "name": col.name,
            "metadata": col.metadata,
            "count": col.count()
        } for col in collections]
