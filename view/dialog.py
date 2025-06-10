import streamlit as st
import re 
import random

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, AIMessageChunk, ToolMessage  # Định dạng tin nhắn

from controller.info_controller import khoi_tao_user_info, display_likert_image, save_feedback
from controller.chat_controller import get_agent_history_from_firebase

from model.sms_OTP import send_OTP, send_OTP_test

def is_valid_phone(phone):
    if phone is None or not isinstance(phone, str) or not phone:
        return False  # Handles None, non-strings, and empty strings
    return re.fullmatch(r"\d{10,11}", phone) is not None

def is_valid_email(email):
    return re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email) is not None  # Định dạng email cơ bản

@st.fragment
@st.dialog(" ", width="small")
def setup_log_in_dialog_with_OTP():
    st.markdown(
        """
        <style>
            .centered {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
            }
        </style>
        <div class="centered">
            <img src="https://res.cloudinary.com/day4wv1aw/image/upload/v1741313942/flic_chatbot/OIP-removebg-preview_vrvzha.png" width="200">
        </div>
        """,
        unsafe_allow_html=True
    )
    if 'gui_ma_OTP' not in st.session_state:
        st.session_state.gui_ma_OTP = False
        
    has_error_OTP = False
    # Nhập số điện thoại
    phone = st.text_input("Số điện thoại:", value="", placeholder="Nhập số điện thoại của bạn")
    phone_warning = st.empty()
    
    # Nhập số điện thoại
    ma_OTP = st.text_input("Mã OTP", value="", placeholder="Nhập mã OTP của bạn")
    ma_OTP_warning = st.empty()
    
    if not st.session_state.get('xac_nhan_OTP', False):
        if not st.session_state.get('gui_ma_OTP', True):
            if st.button("Gửi mã"):
                if phone and not is_valid_phone(phone):
                    phone_warning.warning("Số điện thoại không hợp lệ.")
                else:
                    st.session_state.ma_OTP_tao_ra = random.randint(1000, 9999)
                    
                    status_code = send_OTP(st.session_state.ma_OTP_tao_ra, phone)
                    print(status_code)
                    print(type(status_code))

                    if status_code == 100:
                        st.session_state.gui_ma_OTP = True
                        st.rerun()

        if st.session_state.get('gui_ma_OTP', False):
            phone_warning.success("Đã gửi mã xác nhận đến số điện thoại này")
            # st.write(st.session_state.ma_OTP_tao_ra)
            if st.button("Xác nhận"):
                # Thêm kiểm tra để đảm bảo ma_OTP không rỗng và có thể chuyển đổi thành số nguyên
                if ma_OTP.isdigit(): # Kiểm tra xem chuỗi có phải là số không
                    if int(ma_OTP) != st.session_state.ma_OTP_tao_ra: # Chuyển đổi sang int trước khi so sánh
                        ma_OTP_warning.error('Mã OTP không hợp lệ')
                    else:
                        st.session_state.xac_nhan_OTP = True

                        st.rerun()
                else:
                    ma_OTP_warning.error('Vui lòng nhập mã OTP hợp lệ (chỉ chứa số).')
        
    if st.session_state.get('xac_nhan_OTP', False):
        # Nhập tên (bắt buộc)
        name = st.text_input("Tên của bạn:", value="", placeholder="Nhập tên của bạn")
        # name_warning = st.empty()
        
        # Chọn nghề nghiệp
        job = st.radio("Nghề nghiệp:", options=["Người dùng khác","Học viên FLIC", 'Quản lý'], index=None, horizontal = True)
        job_warning = st.empty()

        if st.button("Gửi"):
            has_error = False
        
            # if not name:
            #     name_warning.warning("Vui lòng nhập tên của bạn.")
            #     has_error = True
            
            if not job:
                job_warning.warning("Vui lòng chọn nghề nghiệp.")
                has_error = True

            if not has_error:

                # Khởi tạo user_info
                user_info = khoi_tao_user_info(phone, job, name)             
                
                # Khởi tạo userID, conversationID, botID 
                # Đặt log_in_dialog_display thành False để ngăn dialog hiển thị lại
                id_session_dict = {
                    'userID': phone,
                    'conversationID': f"RAG{phone}",
                    'botID': "chatbotRAG_v1.0.0",
                    'log_in_dialog_display': False,
                }   

                agent_history = get_agent_history_from_firebase(user_info, id_session_dict)

                # khởi tạo state
                st.session_state.agent_history = agent_history
                st.session_state.id_session_dict = id_session_dict
                st.session_state.user_info = user_info
                st.session_state.rating_display = True
                st.session_state.save_cookie = True
                    
                st.rerun()    

@st.fragment
@st.dialog(" ", width="small")
def setup_log_in_dialog():
    st.markdown(
        """
        <style>
            .centered {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
            }
        </style>
        <div class="centered">
            <img src="https://res.cloudinary.com/day4wv1aw/image/upload/v1741313942/flic_chatbot/OIP-removebg-preview_vrvzha.png" width="200">
        </div>
        """,
        unsafe_allow_html=True
    )
    
    with st.form(key='user_info_form'):
        # Nhập số điện thoại
        phone = st.text_input("Số điện thoại:", value="", placeholder="Nhập số điện thoại của bạn")
        phone_warning = st.empty()
        
        # Nhập tên (bắt buộc)
        name = st.text_input("Tên của bạn:", value="", placeholder="Nhập tên của bạn")
        # name_warning = st.empty()
        
        # Chọn nghề nghiệp
        job = st.radio("Nghề nghiệp:", options=["Người dùng khác","Học viên FLIC", 'Quản lý'], index=None, horizontal = True)
        job_warning = st.empty()
        # Nút gửi
        submit_button = st.form_submit_button(label='Gửi')
        
        if submit_button:
            has_error = False
        
            # if not name:
            #     name_warning.warning("Vui lòng nhập tên của bạn.")
            #     has_error = True
            
            if not job:
                job_warning.warning("Vui lòng chọn nghề nghiệp.")
                has_error = True

            if phone and not is_valid_phone(phone):
                phone_warning.warning("Số điện thoại không hợp lệ.")
                has_error = True
                
            if not phone:
                phone_warning.warning("Vui lòng điền số điện thoại.")
                has_error = True

            if not has_error:

                # Khởi tạo user_info
                user_info = khoi_tao_user_info(phone, job, name)             
                
                # Khởi tạo userID, conversationID, botID 
                # Đặt log_in_dialog_display thành False để ngăn dialog hiển thị lại
                id_session_dict = {
                    'userID': phone,
                    'conversationID': f"RAG{phone}",
                    'botID': "chatbotRAG_v1.0.0",
                    'log_in_dialog_display': False,
                }   

                agent_history = get_agent_history_from_firebase(user_info, id_session_dict)

                # khởi tạo state
                st.session_state.agent_history = agent_history
                st.session_state.id_session_dict = id_session_dict
                st.session_state.user_info = user_info
                st.session_state.rating_display = True
                st.session_state.save_cookie = True
                    
                st.rerun()    

@st.fragment
@st.dialog(" ", width="small")
def setup_feedback_dialog():
    st.markdown("""
        <div style="text-align: center;">
            <h2>Bạn đang cảm thấy như thế nào?</h2>
            <p>Chia sẻ của bạn sẽ giúp chúng tôi hiểu bạn hơn và cải thiện dịch vụ để phục vụ bạn tốt hơn.</p>
        </div>
    """, unsafe_allow_html=True)

    display_likert_image('nghiem_tuc')                          

    with st.form(key='user_info_form'):
        # 1. Loại phản hồi
        feedback_type = st.selectbox(
            "Bạn muốn phản hồi về:",
            ["Trải nghiệm sử dụng", "Báo lỗi", "Đề xuất tính năng", "Khác"]
        )

        # 2. Nội dung góp ý
        feedback_content = st.text_area("Nội dung góp ý:", height=100, placeholder="Hãy cho chúng tôi biết suy nghĩ của bạn...")

        # 4. Nút gửi
        submit_button = st.form_submit_button(label='Gửi')
        
        if submit_button:
            # Lưu vào database
            save_feedback(feedback_type, feedback_content)
            
            st.session_state.rating_display = False
            st.session_state.feedback_log_in_dialog_display = False

            st.rerun()  