import streamlit as st  # Dùng để hiển thị lỗi và cache resource
import os  # Thư viện xử lý hệ thống
from dotenv import load_dotenv  # Nạp biến môi trường

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings, HarmBlockThreshold, HarmCategory  # Model và embedding từ Google

# Nạp biến môi trường
load_dotenv()

# API key cho Google Generative AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  

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
def initialize_llm_model():
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
    
    return llm_model