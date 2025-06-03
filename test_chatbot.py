# controller/chat_controller.py
import streamlit as st  # Dùng để hiển thị giao diện và xử lý input
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage # Định dạng tin nhắn
import time  # Tạo hiệu ứng gõ chữ
import pathlib

# model/tools.py
# --- IMPORT CÁC THƯ VIỆN CẦN THIẾT ---
import streamlit as st  # Dùng để hiển thị lỗi và cache resource
import os  # Thư viện xử lý hệ thống
from dotenv import load_dotenv  # Nạp biến môi trường
import pathlib

from langchain_core.tools.retriever import create_retriever_tool  # Tạo công cụ tìm kiếm cho agent
from langgraph.prebuilt import create_react_agent  # Tạo agent dựa trên mô hình React Agent

from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch  # Hỗ trợ vector search với MongoDB
from langchain_core.vectorstores import VectorStoreRetriever  # Xử lý tìm kiếm trên vector store

from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool

from model.llm import initialize_llm_model, initialize_openai_embedding
from model.database import initialize_mongodb, get_BigQuery, get_BigQuery_engine  # Import hàm từ database.py
from model.SQL_tools import BigQueryDescribeTablesTool

from view.css import load_custom_css  # Tải CSS
from view.interface import setup_page, setup_sidebar, setup_chat_interface, setup_introduction  # Thiết lập giao diện

load_dotenv()

# Lấy tên collection ra
MONGO_DB_COLLECTION_NAME = os.getenv('MONGO_DB_COLLECTION_NAME')

# Lấy tên collection ra
MONGO_DB_DOCUMENT = os.getenv('MONGO_DB_DOCUMENT')
MONGO_DB_COLLECTION_NAME = os.getenv('MONGO_DB_COLLECTION_NAME')
MONGO_DB_VECTOR_INDEX = os.getenv('MONGO_DB_VECTOR_INDEX')
MONGO_DB_FULLTEXT_INDEX = os.getenv('MONGO_DB_VECTOR_INDEX')

# Lấy ra prompt và description
description_RAG_tool = pathlib.Path(r"model/prompts/description_RAG_tool.md").read_text(encoding='utf-8')

def initialize_vector_search() -> MongoDBAtlasVectorSearch:
    """
    Khởi tạo Vector Store từ MongoDB và cache trong 24 giờ.
    - MONGO_DB_COLLECTION_NAME: Tên collection trong MongoDB.
    """
    try:
        embeddings = initialize_openai_embedding()  # Lấy embedding
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


def handle_user_input():
    """
    Xử lý input từ người dùng và điều phối giữa Model và View.
    - agent_history: Lịch sử chat.
    - agent_executor: Agent xử lý câu hỏi.
    - userID: ID người dùng.
    - botID: ID chatbot.
    - conversationID: ID cuộc trò chuyện.
    - db: Firestore client.
    """  
    
    # Tạo ô nhập liệu và lấy input từ người dùng
    if user_input:= st.chat_input("Hãy hỏi tôi về Trung tâm Tiếng Anh FLIC!"):
        system_prompt = pathlib.Path(r"model/prompts/system_prompt_sinh_vien copy.md").read_text(encoding='utf-8')

        system_prompt = system_prompt.replace("{so_dien_thoai}", '0919528530')
        
        # Thêm tin nhắn người dùng vào lịch sử
        st.session_state.agent_history.append(HumanMessage(content=user_input))
        
        # Hiển thị tin nhắn người dùng (xử lý xuống dòng)
        message_xuong_dong = user_input.replace("\n", "  \n")
        st.chat_message("human").markdown(message_xuong_dong)

        with st.spinner("Vui lòng chờ trong giây lát..."):  # Hiển thị spinner khi xử lý
            start_time = time.time()
            
            # Chuẩn bị tin nhắn gửi cho agent
            summarized_message = [SystemMessage(content=system_prompt)]
            
            # Đảm bảo agent_history có ít nhất 8 tin nhắn trước khi slice
            if len(st.session_state.agent_history) > 8:
                recent_history = st.session_state.agent_history[-8:]
            else:
                recent_history = st.session_state.agent_history
            
            summarized_message.extend(recent_history)

            
            # Gọi agent để lấy phản hồi
            output = st.session_state.agent_executor.invoke({"messages": summarized_message})
            response = output["messages"][-1].content  # Lấy phản hồi cuối cùng
            response_usage = output["messages"][-1].usage_metadata
            
            st.session_state.agent_history.append(AIMessage(content=response))

            with st.chat_message("assistant"):
                messages_split = response.split(' ')

                full_response = ""
                text_container = st.markdown("")
                
                for word in messages_split:
                    full_response += word + " "
                    text_container.markdown(full_response)
                    time.sleep(0.005)  # Delay 0.02 giây giữa các từ
                                
            st.write(output)    

def setup_chat_interface():
    """
    Thiết lập giao diện chat chính:
    - Hiển thị tin nhắn của bot và người dùng theo định dạng thích hợp.
    """
    if "agent_history" not in st.session_state:
        st.session_state.agent_history = [
            AIMessage(content='Xin chào')
        ]
        # Thiết lập giao diện chat
        
    # Hiển thị lịch sử chat theo định dạng của streamlit chat message
    for msg in st.session_state.agent_history: # Sử dụng enumerate để lấy cả index
        if isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)

        elif isinstance(msg, HumanMessage):
            # Hiển thị tin nhắn người dùng như bình thường
            message_xuong_dong = msg.content.replace("\n", "  \n")
            st.chat_message("human").markdown(message_xuong_dong)
    
    return st.session_state.agent_history


def main():
    """
    Hàm chính để chạy ứng dụng.
    """     
    setup_page()  # Cấu hình trang
    load_custom_css()  # Tải CSS
    setup_sidebar()  # Thiết lập sidebar
    setup_introduction()
    
    # Khởi tạo agent nếu chưa có
    if "agent_executor" not in st.session_state:
        st.session_state.agent_executor = get_llm_and_agent()
    
    setup_chat_interface()
    handle_user_input()
        
if __name__ == "__main__":
    main()  # Chạy ứng dụng