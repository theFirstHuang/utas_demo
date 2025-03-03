from langchain_community.retrievers import WikipediaRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from config.settings import LLM
import json

class WikipediaEnrichmentService:
    def __init__(self):
        self.retriever = WikipediaRetriever()
        self.artist_parser = self._create_artist_parser()
        self.track_parser = self._create_track_parser()
        
    def _format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)
        
    def _create_artist_parser(self):
        prompt = ChatPromptTemplate.from_template(
            """
            "musical_style": "description of their musical style and characteristics",
            "career": "major achievements and milestones",
            "influence": "industry influence and impact",
            "similar_artists": "list of similar artists and reasons",
            "philosophy": "musical philosophy if available"
            
            Also identify:
            - genres: (list)
            - era: (period)
            - primary_style
            - popularity_level: (1-5)

            Format your response as a JSON object with these keys. If information is not available, use null.
            
            Context: {context}
            Artist: {artist_name}
            """
        )
        
        return (
            {"context": self.retriever | self._format_docs, "artist_name": RunnablePassthrough()}
            | prompt
            | LLM
            | StrOutputParser()
        )
        
    def _create_track_parser(self):
        prompt = ChatPromptTemplate.from_template(
            """Based on the provided context about the music track, 
            extract and structure the following information in natural language sentences (100 words maximum in each):
            
            "lyrics": "main theme and meaning of lyrics",
            "composition": "musical elements and composition details",
            "background": "production and recording background",
            "emotion": "emotional tone and mood",
            "usage": "common usage scenarios"

            Also identify:
            - genre: (main genre)
            - moods: (list of mood tags)
            - tempo: (slow/medium/fast)
            - popularity_level: (1-5)
            
            Format as JSON object with these keys. Use null if unavailable.
            Context: {context}
            Track: {track_name}
            Artist: {artist_name}""")
        
        def get_context(input_dict):
            # 确保我们传入的是字符串
            docs = self.retriever.invoke(str(input_dict["track_name"]))
            return self._format_docs(docs)
        
        chain = (
            {
                "context": get_context,
                "track_name": lambda x: x["track_name"],
                "artist_name": lambda x: x["artist_name"]
            }
            | prompt
            | LLM
            | StrOutputParser()
        )
        return chain

    def enrich_artist(self, artist_name: str) -> dict:
        try:
            result = self.artist_parser.invoke(artist_name)
            return json.loads(result)
        except Exception as e:
            print(f"Error enriching artist {artist_name}: {str(e)}")
            return None

    def enrich_track(self, track_name: str, artist_name: str) -> dict:
        result = self.track_parser.invoke({
                "track_name": track_name, 
                "artist_name": artist_name
            })
        return json.loads(result)
        # try:
        #     result = self.track_parser.invoke({
        #         "track_name": track_name, 
        #         "artist_name": artist_name
        #     })
        #     return json.loads(result)
        # except Exception as e:
        #     print(f"Error enriching track {track_name}: {str(e)}")
        #     return None