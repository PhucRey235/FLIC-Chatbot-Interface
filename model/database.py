# model/database.py
# --- IMPORT CÁC THƯ VIỆN CẦN THIẾT ---
import os  # Thư viện xử lý thao tác hệ thống (đọc biến môi trường)
from dotenv import load_dotenv  # Nạp biến môi trường từ file .env
from pymongo import MongoClient  # Kết nối đến MongoDB
from pymongo.server_api import ServerApi  # Định nghĩa API server cho MongoDB
import firebase_admin  # Thư viện để làm việc với Firebase
from firebase_admin import credentials, firestore  # Cấu hình và truy cập Firestore
import streamlit as st  # Dùng để hiển thị lỗi và cache resource
import time  # Tạo timestamp


from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine

# Nạp biến môi trường từ file .env (chỉ cần gọi một lần)
load_dotenv()

# URI để kết nối MongoDB
MONGODB_URI = os.getenv('MONGODB_URI')  

# Firebase credentials
TYPE_FB = os.getenv("TYPE_FB")   
PROJECT_ID_FB = os.getenv("PROJECT_ID_FB")  
PRIVATE_KEY_ID_FB = os.getenv("PRIVATE_KEY_ID_FB")  
PRIVATE_KEY_FB = os.getenv("PRIVATE_KEY_FB").replace("\\n", "\n")
CLIENT_EMAIL_FB = os.getenv("CLIENT_EMAIL_FB")  
CLIENT_ID_FB = os.getenv("CLIENT_ID_FB")  
AUTH_URI_FB = os.getenv("AUTH_URI_FB")  
TOKEN_URI_FB = os.getenv("TOKEN_URI_FB")  
AUTH_PROVIDER_X509_CERT_URL_FB = os.getenv("AUTH_PROVIDER_X509_CERT_URL_FB")  
CLIENT_X509_CERT_URL_FB = os.getenv("CLIENT_X509_CERT_URL_FB")  
UNIVERSE_DOMAIN_FB = os.getenv("UNIVERSE_DOMAIN_FB")  

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

@st.cache_resource(ttl=24*3600, max_entries=1, hash_funcs={MongoClient: lambda client: None})
def initialize_mongodb():
    """
    Khởi tạo kết nối đến MongoDB và cache kết nối trong 24 giờ.
    - ttl=24*3600: Cache tồn tại 24 giờ.
    - max_entries=1: Chỉ lưu một instance (singleton).
    - hash_funcs: Xử lý hash cho MongoClient (vì nó không hash được mặc định).
    """
    for attempt in range(3):  # Thử lại 3 lần
        try:
            client = MongoClient(MONGODB_URI, server_api=ServerApi("1"), serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            return client
        except Exception as e:
            st.warning(f"Thử lại kết nối MongoDB ({attempt + 1}/3): {str(e)}")
            time.sleep(1)  # Chờ 1 giây trước khi thử lại
    st.error("Không thể kết nối đến MongoDB sau 3 lần thử.")
    return None

@st.cache_resource(ttl=24*3600, max_entries=1, show_spinner=False)
def initialize_firebase():
    """
    Khởi tạo kết nối đến Firebase Firestore để lưu trữ lịch sử trò chuyện.
    - Chỉ khởi tạo một lần duy nhất nếu chưa có ứng dụng Firebase nào tồn tại.
    """
    if not firebase_admin._apps:  # Kiểm tra xem Firebase đã khởi tạo chưa
        # Đường dẫn đến file chứng chỉ Firebase (cần thay đổi theo máy của bạn)
        cred = credentials.Certificate({
            "type": TYPE_FB,
            "project_id": PROJECT_ID_FB,
            "private_key_id": PRIVATE_KEY_ID_FB,
            "private_key": PRIVATE_KEY_FB,
            "client_email": CLIENT_EMAIL_FB,
            "client_id": CLIENT_ID_FB,
            "auth_uri": AUTH_URI_FB,
            "token_uri": TOKEN_URI_FB,
            "auth_provider_x509_cert_url": AUTH_PROVIDER_X509_CERT_URL_FB,
            "client_x509_cert_url": CLIENT_X509_CERT_URL_FB,
            "universe_domain": UNIVERSE_DOMAIN_FB,
        })
        firebase_admin.initialize_app(cred)  # Khởi tạo ứng dụng Firebase
    return firestore.client()  # Trả về Firestore client để truy cập database   
        
@st.cache_resource(ttl=24*3600, max_entries=1, show_spinner=False)
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