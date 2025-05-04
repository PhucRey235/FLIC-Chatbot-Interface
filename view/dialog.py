import streamlit as st
import re 

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, AIMessageChunk, ToolMessage  # Định dạng tin nhắn

from controller.info_controller import khoi_tao_customized_prompt, display_likert_image, save_feedback
from controller.chat_controller import get_agent_history_from_firebase

def is_valid_phone(phone):
    return re.fullmatch(r"\d{10,11}", phone) is not None  # SĐT phải có 10-11 chữ số

def is_valid_email(email):
    return re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email) is not None  # Định dạng email cơ bản

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
        job = st.radio("Nghề nghiệp:", options=["Sinh viên","Học viên FLIC", "Khác"], index=None, horizontal = True)
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

            if not has_error:

                # Khởi tạo customized_prompt
                customized_prompt, user_info = khoi_tao_customized_prompt(phone, job, name)             
                
                # Khởi tạo userID, conversationID, botID 
                # Đặt log_in_dialog_display thành False để ngăn dialog hiển thị lại
                id_session_dict = {
                    'userID': phone,
                    'conversationID': f"RAG{phone}",
                    'botID': "chatbotRAG_v1.0.0",
                    'log_in_dialog_display': False,
                    'customized_prompt': customized_prompt.replace("\n", ""),
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