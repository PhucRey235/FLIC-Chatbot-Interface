# main.py
import streamlit as st  # Dùng để chạy ứng dụng
from dotenv import load_dotenv
import os

from view.css import load_custom_css  # Tải CSS
from view.interface import setup_page, setup_sidebar, setup_chat_interface, setup_chat_interface_with_employee, setup_introduction  # Thiết lập giao diện
from view.dialog import setup_log_in_dialog, setup_feedback_dialog

from model.database import initialize_firebase  # Khởi tạo Firebase
from model.tools import get_llm_and_agent, get_llm_and_agent_hoc_vien  # Khởi tạo agent

from controller.chat_controller import handle_user_input, handle_user_input_with_employee  # Xử lý input
from controller.cookie import get_cookie_data, setup_cookie_data
from controller.on_snapshot_controller import start_chat_monitoring, process_queue_and_update_state


load_dotenv()

# Lấy tên collection ra
MONGO_DB_COLLECTION_NAME = os.getenv('MONGO_DB_COLLECTION_NAME')

def main():
    """
    Hàm chính để chạy ứng dụng.
    """      
    setup_page()  # Cấu hình trang
    load_custom_css()  # Tải CSS
    setup_sidebar()  # Thiết lập sidebar
    setup_introduction()
    
    # Khởi tạo Firebase nếu chưa có
    if "firebase_db" not in st.session_state:
        st.session_state.firebase_db = initialize_firebase()
        
    if 'user_info' not in st.session_state:
        get_cookie_data()
         
    # Hiển thị dialog nếu chưa có
    if st.session_state.get('id_session_dict', {}).get('log_in_dialog_display', True):
        setup_log_in_dialog()
    
    if st.session_state.get('save_cookie', False):
        setup_cookie_data()
        
    if (not st.session_state.get('user_info', {}).get('la_hoc_vien', True) 
        and st.session_state.get('user_info', {}).get('job', 'người dùng ẩn danh') == 'Học viên FLIC'):
        st.warning('Tôi không tìm thấy thông tin học viên của bạn, bạn có thể sửa lại thông tin')

        if st.button("Điền thông tin"):
            setup_log_in_dialog()

    # Khởi tạo agent nếu chưa có
    if "agent_executor" not in st.session_state:
        # if not st.session_state.get('user_info', {}).get('la_hoc_vien', True):
        #     st.session_state.agent_executor = get_llm_and_agent()
        # elif st.session_state.get('user_info', {}).get('la_hoc_vien', False):
        st.session_state.agent_executor = get_llm_and_agent_hoc_vien()
            
    if "agent_history" in st.session_state and not st.session_state.get('gap_nhan_vien', False):
        st.session_state.agent_history = setup_chat_interface()  # Thiết lập giao diện chat
        
    elif "agent_history" in st.session_state and st.session_state.get('gap_nhan_vien', False):
        start_chat_monitoring()
        process_queue_and_update_state()
        
        st.session_state.agent_history = setup_chat_interface_with_employee()
        
    else:
        st.chat_message("assistant").write("Tôi có thể giúp gì cho bạn?")   

    # Khởi tạo cờ is_processing nếu chưa có
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    
    if st.session_state.get('gap_nhan_vien', False):        
        handle_user_input_with_employee()
    else:
        # Xử lý input người dùng
        handle_user_input()
        
if __name__ == "__main__":
    main()  # Chạy ứng dụng