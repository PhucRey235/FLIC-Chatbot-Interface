# model/tools.py
# --- IMPORT CÁC THƯ VIỆN CẦN THIẾT ---
import streamlit as st  # Dùng để hiển thị lỗi và cache resource
import os  # Thư viện xử lý hệ thống
from dotenv import load_dotenv  # Nạp biến môi trường

from langchain_core.tools.retriever import create_retriever_tool  # Tạo công cụ tìm kiếm cho agent
from langgraph.prebuilt import create_react_agent  # Tạo agent dựa trên mô hình React Agent

from langchain_community.retrievers import MongoDBAtlasHybridSearchRetriever
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch  # Hỗ trợ vector search với MongoDB
from langchain_core.vectorstores import VectorStoreRetriever  # Xử lý tìm kiếm trên vector store
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings, HarmBlockThreshold, HarmCategory  # Model và embedding từ Google

from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine

from .database import initialize_mongodb  # Import hàm từ database.py

# Nạp biến môi trường
load_dotenv()

# Lấy tên collection ra
MONGO_DB_DOCUMENT = os.getenv('MONGO_DB_DOCUMENT')
MONGO_DB_COLLECTION_NAME = os.getenv('MONGO_DB_COLLECTION_NAME')
MONGO_DB_VECTOR_INDEX = os.getenv('MONGO_DB_VECTOR_INDEX')
MONGO_DB_FULLTEXT_INDEX = os.getenv('MONGO_DB_VECTOR_INDEX')

# API key cho Google Generative AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  

# Bigquery credentials
TYPE_BQ = os.getenv("TYPE_BQ")   
PROJECT_ID_BQ = os.getenv("PROJECT_ID_BQ")  
PRIVATE_KEY_ID_BQ = os.getenv("PRIVATE_KEY_ID_BQ")  
PRIVATE_KEY_BQ = os.getenv("PRIVATE_KEY_BQ").replace("\\n", "\n")
CLIENT_EMAIL_BQ = os.getenv("CLIENT_EMAIL_BQ")  
CLIENT_ID_BQ = os.getenv("CLIENT_ID_BQ")  
AUTH_URI_BQ = os.getenv("AUTH_URI_BQ")  
TOKEN_URI_BQ = os.getenv("TOKEN_URI_BQ")  
AUTH_PROVIDER_X509_CERT_URL_BQ = os.getenv("AUTH_PROVIDER_X509_CERT_URL_BQ")  
CLIENT_X509_CERT_URL_BQ = os.getenv("CLIENT_X509_CERT_URL_BQ")  
UNIVERSE_DOMAIN_BQ = os.getenv("UNIVERSE_DOMAIN_BQ")  

# Database của BigQuery
DATASET_ID_BQ = os.getenv("DATASET_ID_BQ")  

@st.cache_resource(ttl=24*3600, max_entries=1, show_spinner=False)
def initialize_embedding(model_name: str = 'models/text-embedding-004') -> GoogleGenerativeAIEmbeddings:
    """
    Khởi tạo model embedding từ Google Generative AI và cache trong 24 giờ.
    - model_name: Tên model embedding mặc định.
    """
    try:
        # Tạo instance embedding với model và API key
        return GoogleGenerativeAIEmbeddings(model=model_name, google_api_key=GOOGLE_API_KEY)
    except Exception as e:
        # Hiển thị lỗi nếu khởi tạo thất bại
        st.error(f"Lỗi khởi tạo embedding model: {str(e)}")
        return None

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
            relevance_score_fn='euclidean' # euclidean | cosine | dotProduct  # Hàm tính điểm liên quan
        )
    except Exception as e:
        st.error(f"Lỗi khởi tạo vector store: {str(e)}")
        return None

@st.cache_resource(show_spinner=False)
def initialize_hybrid_search() -> MongoDBAtlasHybridSearchRetriever:
    """
    Lấy Hybrid Search Retriever từ MongoDB và cache trong 24 giờ.
    """
    try:
        vector_search = initialize_vector_search()
        
        if vector_search is None:
            return None

        hybrid_search = MongoDBAtlasHybridSearchRetriever(
            vectorstore=vector_search,
            search_index_name=MONGO_DB_FULLTEXT_INDEX,
            vector_penalty=60.0,  # Điều chỉnh trọng số của vector search
            fulltext_penalty=60.0,  # Điều chỉnh trọng số của full-text search
            top_k=10,  # Số lượng kết quả trả về
        )
        
        return hybrid_search
    except Exception as e:
        st.error(f"Lỗi khởi tạo Hybrid Search retriever: {str(e)}")
        return None

@st.cache_resource(ttl=24*3600, max_entries=1, show_spinner=False, hash_funcs={"_RetrieverType": lambda x: None})
def get_mongodb_retriever() -> VectorStoreRetriever:
    """
    Lấy retriever từ Vector Store và cache trong 24 giờ.
    - MONGO_DB_COLLECTION_NAME: Tên collection trong MongoDB.
    - hash_funcs: Xử lý hash cho retriever (vì nó không hash được mặc định).
    """
    try:
        hybrid_search = initialize_hybrid_search()  # Lấy Vector Store
        
        if hybrid_search is None:
            return None
        # Tạo retriever với tìm kiếm similarity, trả về 4 kết quả
        return hybrid_search.as_retriever(
            search_type="similarity", 
            search_kwargs={"k": 5,}
        )
    except Exception as e:
        st.error(f"Lỗi khởi tạo retriever: {str(e)}")
        return None
    

    
    
    

# Hệ thống prompt hướng dẫn chatbot
system_prompt = ("""
Bạn là một trợ lý ảo được trang bị các công cụ RAG và SQL Toolkit (Chỉ dành cho học viên đối với SQL Toolkit) để hỗ trợ khách hàng của Trung tâm Tiếng Anh FLIC. Hãy trả lời các câu hỏi một cách trang trọng và cung cấp thông tin chính xác về trung tâm.

Khi nhận được câu hỏi, hãy xem xét các trường hợp sau:

1.  **Câu hỏi chung về khóa học, kỳ thi CNTT và TOEIC, lịch thi, lệ phí, thủ tục đăng ký, nội dung đào tạo, ưu đãi:** Sử dụng công cụ **RAG** để tìm kiếm thông tin liên quan và trả lời.
2.  **(Chỉ dành cho học viên, nếu được cung cấp đây là học viên và mã định danh):** **Câu hỏi về thông tin cá nhân của học viên, điểm thi:** Sử dụng công cụ **SQL Toolkit** để truy vấn cơ sở dữ liệu và cung cấp thông tin.
3.  **Câu hỏi cơ bản khác về trung tâm:** Trả lời trực tiếp nếu bạn có thông tin.

**Lưu ý quan trọng:**

* Khi sử dụng các công cụ, bạn không cần phải xin phép người dùng hoặc thông báo rằng bạn đang sử dụng công cụ. Chỉ cần cung cấp câu trả lời dựa trên kết quả từ công cụ.

**Thông tin bổ sung:**

* Hãy coi "Chứng chỉ CNTT", "Công nghệ Thông tin" và "Tin học" là một khái niệm.
* Luôn khuyến khích người dùng đăng ký khóa học theo nhóm để nhận ưu đãi.

**Trường hợp không thể trả lời:**

* Nếu người dùng hỏi về các kỳ thi A1, A2, B1, B2, C1, C2, hãy trả lời: "Hiện tại, trung tâm chỉ cung cấp khóa học và tổ chức kỳ thi TOEIC phối hợp với IIG Việt Nam, chưa có chương trình dành cho kỳ thi đó. Nếu bạn quan tâm đến luyện thi TOEIC, chúng tôi có các khóa học phù hợp và hỗ trợ đăng ký thi chính thức."
* Nếu bạn không tìm thấy thông tin cụ thể cho câu hỏi của người dùng, hãy lịch sự hướng dẫn họ liên hệ trực tiếp với Trung tâm Tiếng Anh FLIC để được hỗ trợ thêm.
""")

def get_BigQuery_engine():
    credentials_info = {
        "type": TYPE_BQ,
        "project_id": PROJECT_ID_BQ,
        "private_key_id": PRIVATE_KEY_ID_BQ,
        "private_key": PRIVATE_KEY_BQ,
        "client_email": CLIENT_EMAIL_BQ,
        "client_id": CLIENT_ID_BQ,
        "auth_uri": AUTH_URI_BQ,
        "token_uri": TOKEN_URI_BQ,
        "auth_provider_x509_cert_url": AUTH_PROVIDER_X509_CERT_URL_BQ,
        "client_x509_cert_url": CLIENT_X509_CERT_URL_BQ,
        "universe_domain": UNIVERSE_DOMAIN_BQ,
    }   

    engine = create_engine(
        url = f"bigquery://{PROJECT_ID_BQ}/{DATASET_ID_BQ}",
        credentials_info = credentials_info,
    )
    
    Bigquery_db = SQLDatabase(engine=engine)
    
    return Bigquery_db

@st.cache_resource(ttl=24*3600, max_entries=1, show_spinner=False)
def check_phone_in_database(so_dien_thoai: str):
    # Hàm kiểm tra số điện thoại trong cơ sở dữ liệu BigQuery
    Bigquery_db = get_BigQuery_engine()  # Lấy kết nối BigQuery
    query = f"SELECT phone FROM students WHERE phone = '{so_dien_thoai}' LIMIT 1"
    result = Bigquery_db.run(query)  # Thực hiện truy vấn
    return len(result) > 0  #  Trả về True nếu tìm thấy số điện thoại

def get_llm_and_agent():
    """
    Khởi tạo Language Model và Agent, sau đó cache trong 24 giờ.
    - MONGO_DB_COLLECTION_NAME: Tên collection trong MongoDB.
    """
    try:
        # Tạo model Gemini với các tham số cấu hình
        llm_model = ChatGoogleGenerativeAI(
            model="models/gemini-2.0-flash",  # Model Gemini
            temperature=0.3,  # Độ sáng tạo (0-1)
            max_tokens=1000,  # Số token tối đa trong phản hồi
            timeout=10,  # Thời gian chờ tối đa
            max_retries=2,  # Số lần thử lại nếu lỗi
            api_key=GOOGLE_API_KEY,
            safety_settings={  # Cấu hình chặn nội dung không phù hợp
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH
            }
        )

        retriever = get_mongodb_retriever()  # Lấy retriever

        if retriever is None:
            st.error("Không thể khởi tạo agent do lỗi retriever")
            return None
        # Tạo công cụ tìm kiếm cho agent
        retriever_tool = create_retriever_tool(
            retriever=retriever,
            name='RAG',
            description=(
                "Công cụ tìm kiếm để lấy thông tin cơ bản về trung tâm từ hệ thống RAG (MongoDB), như: "
                "chính sách, khóa học, lịch thi, lệ phí, thủ tục đăng ký, nội dung đào tạo, ưu đãi, "
                "hỗ trợ chatbot trả lời câu hỏi một cách chính xác và nhanh chóng."  # Mô tả cập nhật để phân biệt với SQL
            )   
        )

        Bigquery_db = get_BigQuery_engine()

        toolkit = SQLDatabaseToolkit(db=Bigquery_db, llm=llm_model)

        tools =  [retriever_tool] + toolkit.get_tools() # Danh sách công cụ cho agent
        # Tạo agent với model và tools
        agent_executor = create_react_agent(model=llm_model, tools=tools, prompt=system_prompt)

        return agent_executor
    
    except Exception as e:
        st.error(f"Lỗi khởi tạo agent: {str(e)}")
        print(f"Lỗi khởi tạo agent: {str(e)}")
        return None
