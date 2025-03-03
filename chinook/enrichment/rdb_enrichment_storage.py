# enrichment/storage_service.py

import json
from typing import Dict, Any
from database.connection import get_db

class RDBEnrichmentStorageService:
    """Service for storing enrichment data in both RDB and VDB"""
    
    def __init__(self):
        self.db = get_db()

    def _escape_string(self, value):
        """Escape string values for SQL insertion"""
        if value is None:
            return 'NULL'
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        # 替换单引号和其他特殊字符
        return str(value).replace("'", "''")

    def _store_metadata(self, table: str, entity_id: int, metadata: Dict[str, Any]):
        """Store metadata in RDB using key-value pairs"""
        for key, value in metadata.items():
            if value is None:
                continue
                
            # 使用直接的字符串转义而不是参数化查询
            escaped_value = self._escape_string(value)
            
            sql = f"""
            INSERT INTO {table} (
                {table.split('_')[0]}_id,
                meta_key,
                meta_value
            ) VALUES (
                {entity_id},
                '{self._escape_string(key)}',
                '{escaped_value}'
            ) ON DUPLICATE KEY UPDATE
                meta_value = '{escaped_value}'
            """
            self.db.run(sql)

    def store_artist_enrichment(self, artist_id: int, data: Dict[str, Any]):
        """Store artist enrichment data in both RDB and VDB"""
        try:
            # Store in RDB
            rdb_metadata = {
                'genres': data.get('genres'),
                'era': data.get('era'),
                'primary_style': data.get('primary_style'),
                'popularity_level': data.get('popularity_level')
            }
            self._store_metadata('artist_metadata', artist_id, rdb_metadata)
            
            # # Store in VDB
            # vdb_content = f"""
            # Musical Style: {data.get('musical_style_description')}
            # Career Highlights: {data.get('career_highlights')}
            # Industry Influence: {data.get('influence_description')}
            # Similar Artists: {data.get('similar_artists_description')}
            # Musical Philosophy: {data.get('musical_philosophy')}
            # """
            
            # vector_doc = VectorDocument.create(
            #     content=vdb_content.strip(),
            #     metadata={
            #         "artist_id": artist_id,
            #         "doc_type": "artist_enrichment",
            #         **rdb_metadata  # Include shared metadata
            #     }
            # )
            
            # self.artist_store.add_documents([vector_doc])
            
        except Exception as e:
            print(f"Error storing artist enrichment: {str(e)}")
            raise

    def store_track_enrichment(self, track_id: int, data: Dict[str, Any]):
        """Store track enrichment data in both RDB and VDB"""
        try:
            # Store in RDB
            print(f"data is : \n{data}")
            rdb_metadata = {
                'genre': data.get('genre'),
                'moods': data.get('moods'),
                'tempo': data.get('tempo'),
                'popularity_level': data.get('popularity_level')
            }
            self._store_metadata('track_metadata', track_id, rdb_metadata)
            
            # # Store in VDB
            # vdb_content = f"""
            # Lyrics Theme: {data.get('lyrics_theme')}
            # Musical Elements: {data.get('musical_elements')}
            # Production Background: {data.get('production_background')}
            # Emotional Tone: {data.get('emotional_tone')}
            # Usage Scenarios: {data.get('usage_scenarios')}
            # """
            
            # vector_doc = VectorDocument.create(
            #     content=vdb_content.strip(),
            #     metadata={
            #         "track_id": track_id,
            #         "doc_type": "track_enrichment",
            #         **rdb_metadata  # Include shared metadata
            #     }
            # )
            
            # self.track_store.add_documents([vector_doc])
            
        except Exception as e:
            print(f"Error storing track enrichment: {str(e)}")
            raise