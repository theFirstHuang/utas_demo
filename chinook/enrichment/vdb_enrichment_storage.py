# enrichment/vdb_enrichment_storage.py

from typing import Dict, Any
from vector_storage.models import VectorDocument, VectorStore
from config.settings import COLLECTION_NAMES

class VDBEnrichmentStorageService:
    """Service for storing enrichment data in vector database"""
    
    def __init__(self):
        self.artist_store = VectorStore(COLLECTION_NAMES["ARTIST"])
        self.track_store = VectorStore(COLLECTION_NAMES["TRACK"])
    
    def store_artist_enrichment(self, artist_id: int, data: Dict[str, Any]):
        """Store artist enrichment data in VDB"""
        try:
            # 准备meta
            shared_metadata = clean_metadata({
                'genres': data.get('genres'),
                'era': data.get('era'),
                'primary_style': data.get('primary_style'),
                'popularity_level': data.get('popularity_level'),
                'pop_tier' : data.get('pop_tier')
            })
            
            # 准备content
            vdb_content = f"""
            Musical Style: {data.get('musical_style_description')}
            Career Highlights: {data.get('career_highlights')}
            Industry Influence: {data.get('influence_description')}
            Similar Artists: {data.get('similar_artists_description')}
            Musical Philosophy: {data.get('musical_philosophy')}
            """
            
            # 创建doc
            vector_doc = VectorDocument.create(
                content=vdb_content.strip(),
                metadata={
                    "artist_id": artist_id,
                    "doc_type": "artist_enrichment",
                    **shared_metadata  # 包含共享元数据
                }
            )
            
            self.artist_store.add_documents([vector_doc])
            
        except Exception as e:
            print(f"Error storing artist enrichment in VDB: {str(e)}")
            raise

    def store_track_enrichment(self, track_id: int, data: Dict[str, Any]):
        """Store track enrichment data in VDB"""
        try:
            # 准备meta
            shared_metadata = clean_metadata({
                'genre_classification': data.get('genre_classification'),
                'mood_tags': data.get('mood_tags'),
                'tempo_category': data.get('tempo_category'),
                'popularity_level': data.get('popularity_level')
            })
            
            # 准备content
            vdb_content = f"""
            Lyrics Theme: {data.get('lyrics_theme')}
            Musical Elements: {data.get('musical_elements')}
            Production Background: {data.get('production_background')}
            Emotional Tone: {data.get('emotional_tone')}
            Usage Scenarios: {data.get('usage_scenarios')}
            """
            
            # 创建doc
            vector_doc = VectorDocument.create(
                content=vdb_content.strip(),
                metadata={
                    "track_id": track_id,
                    "doc_type": "track_enrichment",
                    **shared_metadata  # 包含共享元数据
                }
            )
            
            self.track_store.add_documents([vector_doc])
            
        except Exception as e:
            print(f"Error storing track enrichment in VDB: {str(e)}")
            raise
            
    def get_artist_enrichment(self, artist_id: int) -> Dict:
        """获取艺术家的向量存储数据"""
        try:
            results = self.artist_store.search(
                query="",
                metadata_filter={"artist_id": artist_id}
            )
            return results[0] if results else None
        except Exception as e:
            print(f"Error retrieving artist enrichment from VDB: {str(e)}")
            return None
            
    def get_track_enrichment(self, track_id: int) -> Dict:
        """获取音轨的向量存储数据"""
        try:
            results = self.track_store.search(
                query="",
                metadata_filter={"track_id": track_id}
            )
            return results[0] if results else None
        except Exception as e:
            print(f"Error retrieving track enrichment from VDB: {str(e)}")
            return None
    
def clean_metadata(data):
    """
    递归处理字典中的None值,将其转换为'null'字符串。
    适用于向量数据库元数据处理。
    
    Args:
        data: 需要处理的数据，可以是字典、列表或单个值
        
    Returns:
        处理后的数据, 所有None值都被替换为'null'
    """
    if isinstance(data, dict):
        return {k: clean_metadata(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_metadata(v) for v in data]
    elif data is None:
        return 'null'
    return data