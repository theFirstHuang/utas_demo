import json
import streamlit as st
import pandas as pd
from vector_storage.connection import ChromaDBConnection
from config.settings import COLLECTION_NAMES

def visualize_chroma_collections():
    vdb = ChromaDBConnection()
    client = vdb.get_client()
    collection = client.get_collection(COLLECTION_NAMES["TRACK"])
    
    # 获取所有数据
    results = collection.get()
    
    # 将metadata转换为字符串形式
    metadatas_str = [json.dumps(m, ensure_ascii=False) for m in results['metadatas']]
    
    # 创建DataFrame
    df = pd.DataFrame({
        'documents': results['documents'],
        'metadatas': metadatas_str
    })
    
    # 显示数据
    st.title("ChromaDB Collection Viewer")
    st.dataframe(df)
    
    # 添加一些交互式过滤选项
    if len(results['metadatas']) > 0:
        # 从metadata中提取可能的过滤字段
        sample_metadata = results['metadatas'][0]
        for key in sample_metadata.keys():
            unique_values = set(m.get(key) for m in results['metadatas'])
            if len(unique_values) < 10:  # 只为较少的唯一值创建过滤器
                selected_value = st.selectbox(f"Filter by {key}", ["All"] + list(unique_values))
                if selected_value != "All":
                    df = df[df['metadatas'].apply(lambda x: json.loads(x).get(key) == selected_value)]
                    st.dataframe(df)

if __name__ == "__main__":
    visualize_chroma_collections()