import time
from typing import Dict, Any
from config.settings import COLLECTION_NAMES
from enrichment.rdb_enrichment_storage import RDBEnrichmentStorageService
from enrichment.vdb_enrichment_storage import VDBEnrichmentStorageService
from vector_storage.models import VectorDocument, VectorStore
from database.connection import get_db
from database.running_log_model import RunningLog
from chains.intent_chain import IntentClarificationChain
from chains.sql_chain import SQLChain
from chains.optimization_chain import QueryOptimizationChain
from chains.feedback_chain import FeedbackChain
from chains.response_chain import ResponseChain
from enrichment.wiki_enrichment_service import WikipediaEnrichmentService
from vdb_visualisation import visualize_chroma_collections

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

                    if result:
                        # 5. generate human response
                        print('Running Success after optimization')
                        print('--- RUNNING Chain 5: response chain')
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
    question = "哪些音乐在普通工作日的工作时间9-17点的销量特别好?"
    chain = FullChain()
    # result = chain.process_question(
    #     question
    # )
    # print(result)

    # useable questions list
    """
    我想要知道最有激情的音乐中卖的最多是哪一个
    - Which artist is the fan-favorite based on sales?
    - 最能带动学生聚会气氛的音乐类型是什么？
    - Which genre gets students most excited? 
    - 用户最常单独购买的歌曲是哪些？
    - 每个国家销售额最高的音乐类型是什么？
    - 最容易让用户重复购买的专辑类型是什么
    - 哪些音乐在普通工作日的工作时间段的销量特别好？
    """

#     # 创建向量存储实例
#     artist_store = VectorStore(COLLECTION_NAMES["ARTIST"])

#     # 创建示例文档
#     doc = VectorDocument(
#         doc_id="artist_2",
#         content="""AC/DC is a legendary Australian rock band formed in Sydney in 1973 by brothers Malcolm and Angus Young. Known for their high-energy performances and electrifying sound, AC/DC has become one of the most influential bands in rock history. Their music is characterized by powerful guitar riffs, driving rhythms, and unforgettable hooks, blending hard rock with blues influences.

# The band's early success came with albums like High Voltage and Let There Be Rock, but it was their 1980 album, Back in Black, that propelled them to global stardom. This album, released as a tribute to their late lead singer Bon Scott, became one of the best-selling records of all time.""",
#         metadata={
#             "artist_id": "1",
#             "doc_type": "biography",
#             "era": "1970s",
#             "genres": "jazz",
#             "source": "wiki"
#         }
#     )

#     # 添加文档
#     artist_store.add_documents([doc])

#     # 搜索相似文档
    # artist_store = VectorStore(COLLECTION_NAMES["ARTIST"])
    # results = artist_store.search("70s Australia music", n_results=5)
    # print(results)
    # # 查看所有集合
    # collections = VectorStore.list_collections()
    # for collection in collections:
    #     print(f"集合名称: {collection['name']}")
    #     print(f"元数据: {collection['metadata']}")
    #     print(f"文档数量: {collection['count']}")
    #     print("---")

#wiki retriever test
    service = WikipediaEnrichmentService()
    storage_service = RDBEnrichmentStorageService()
    vdb_storage = VDBEnrichmentStorageService()
    artist_name = "Accept"
    track_name = "For Those About To Rock (We Salute You)"
    artist_id = 2
    track_id = 1
    result = service.enrich_artist(artist_name)
    #result = service.enrich_track(track_name, artist_name)
    print(result)
    vdb_storage.store_artist_enrichment(artist_id,result)
    storage_service.store_track_enrichment(track_id, result)
    print("Finished")
