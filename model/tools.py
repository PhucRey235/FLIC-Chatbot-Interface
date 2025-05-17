# model/tools.py
# --- IMPORT CÁC THƯ VIỆN CẦN THIẾT ---
import streamlit as st  # Dùng để hiển thị lỗi và cache resource
import os  # Thư viện xử lý hệ thống
from dotenv import load_dotenv  # Nạp biến môi trường
    
from langchain_core.tools.retriever import create_retriever_tool  # Tạo công cụ tìm kiếm cho agent
from langgraph.prebuilt import create_react_agent  # Tạo agent dựa trên mô hình React Agent

from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch  # Hỗ trợ vector search với MongoDB
from langchain_core.vectorstores import VectorStoreRetriever  # Xử lý tìm kiếm trên vector store

from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool

from .llm import initialize_embedding, initialize_llm_model
from .database import initialize_mongodb, get_BigQuery, get_BigQuery_engine  # Import hàm từ database.py
from .SQL_tools import BigQueryDescribeTablesTool

import pathlib

# Nạp biến môi trường
load_dotenv()

# Lấy tên collection ra
MONGO_DB_DOCUMENT = os.getenv('MONGO_DB_DOCUMENT')
MONGO_DB_COLLECTION_NAME = os.getenv('MONGO_DB_COLLECTION_NAME')
MONGO_DB_VECTOR_INDEX = os.getenv('MONGO_DB_VECTOR_INDEX')
MONGO_DB_FULLTEXT_INDEX = os.getenv('MONGO_DB_VECTOR_INDEX')

# Lấy ra prompt và description
description_RAG_tool = pathlib.Path("model/prompts/description_RAG_tool.md").read_text(encoding='utf-8')

@st.cache_resource(ttl=24*3600, max_entries=1, show_spinner=False)
def initialize_vector_search() -> MongoDBAtlasVectorSearch:
    """
    Khởi tạo Vector Store từ MongoDB và cache trong 24 giờ.
    - MONGO_DB_COLLECTION_NAME: Tên collection trong MongoDB.
    """
    try:
        embeddings = initialize_embedding()  # Lấy embedding
        if embeddings is None:
            return None
        client = initialize_mongodb()  # Lấy kết nối MongoDB
        if client is None:
            return None
        collection = client[MONGO_DB_DOCUMENT][MONGO_DB_COLLECTION_NAME]  # Chọn collection
        # Tạo Vector Store với các tham số cần thiết
        return MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embeddings,
            text_key='content',  # Trường chứa văn bản trong MongoDB
            embedding_key='embedding',  # Trường chứa vector embedding
            index_name=MONGO_DB_VECTOR_INDEX,  # Tên index vector
            relevance_score_fn='dotProduct' # euclidean | cosine | dotProduct  # Hàm tính điểm liên quan
        )
    except Exception as e:
        st.error(f"Lỗi khởi tạo vector store: {str(e)}")
        return None

@st.cache_resource(ttl=24*3600, max_entries=1, show_spinner=False, hash_funcs={"_RetrieverType": lambda x: None})
def get_mongodb_retriever() -> VectorStoreRetriever:
    """
    Lấy retriever từ Vector Store và cache trong 24 giờ.
    - MONGO_DB_COLLECTION_NAME: Tên collection trong MongoDB.
    - hash_funcs: Xử lý hash cho retriever (vì nó không hash được mặc định).
    """
    try:
        vector_search = initialize_vector_search()  # Lấy Vector Store
        
        if vector_search is None:
            return None
        # Tạo retriever với tìm kiếm similarity, trả về 4 kết quả
        return vector_search.as_retriever(
            search_type="similarity", 
            search_kwargs={"k": 5,}
        )
    except Exception as e:
        st.error(f"Lỗi khởi tạo retriever: {str(e)}")
        return None

@st.cache_resource(ttl=24*3600, max_entries=1, show_spinner=False)
def get_llm_and_agent():
    """
    Khởi tạo Language Model và Agent, sau đó cache trong 24 giờ.
    - MONGO_DB_COLLECTION_NAME: Tên collection trong MongoDB.
    """
    try:
        llm_model = initialize_llm_model()

        retriever = get_mongodb_retriever()  # Lấy retriever

        if retriever is None:
            st.error("Không thể khởi tạo agent do lỗi retriever")
            return None
        # Tạo công cụ tìm kiếm cho agent
        retriever_tool = create_retriever_tool(
            retriever=retriever,
            name='RAG',
            description=description_RAG_tool
        )

        tools =  [retriever_tool] # Danh sách công cụ cho agent
        # Tạo agent với model và tools
        agent_executor = create_react_agent(model=llm_model, tools=tools)

        return agent_executor

    except Exception as e:
        st.error(f"Lỗi khởi tạo agent: {str(e)}")
        print(f"Lỗi khởi tạo agent: {str(e)}")
        return None

@st.cache_resource(ttl=24*3600, max_entries=1, show_spinner=False)
def get_llm_and_agent_hoc_vien():
    """
    Khởi tạo Language Model và Agent, sau đó cache trong 24 giờ.
    - MONGO_DB_COLLECTION_NAME: Tên collection trong MongoDB.
    """
    try:
        llm_model = initialize_llm_model()

        retriever = get_mongodb_retriever()  # Lấy retriever

        if retriever is None:
            st.error("Không thể khởi tạo agent do lỗi retriever")
            return None
        # Tạo công cụ tìm kiếm cho agent
        retriever_tool = create_retriever_tool(
            retriever=retriever,
            name='RAG',
            description=description_RAG_tool
        )

        client, project_id, dataset_id = get_BigQuery()

        describe_tool = BigQueryDescribeTablesTool(client=client, project_id=project_id, dataset_id=dataset_id)

        query_tool = QuerySQLDatabaseTool(db=get_BigQuery_engine())

        tools =  [retriever_tool, describe_tool, query_tool] # Danh sách công cụ cho agent
        
        # Tạo agent với model và tools
        agent_executor = create_react_agent(model=llm_model, tools=tools)

        return agent_executor

    except Exception as e:
        st.error(f"Lỗi khởi tạo agent: {str(e)}")
        print(f"Lỗi khởi tạo agent: {str(e)}")
        return None