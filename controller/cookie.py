import streamlit as st
import json
from streamlit_js_eval import get_cookie, set_cookie
from streamlit_javascript import st_javascript

from langchain_core.messages import HumanMessage, AIMessage  # Định dạng tin nhắn
from controller.chat_controller import get_agent_history_from_firebase

# Giả sử bạn đã import hoặc định nghĩa lớp HumanMessage và AIMessage ở đâu đó:
# from your_module import HumanMessage, AIMessage

def serialize_history(history):
    """
    Chuyển list các đối tượng (HumanMessage, AIMessage) thành JSON string.
    """
    serializable_history = []
    for msg in history:
        if hasattr(msg, 'content'):
            # Xác định loại của message để lưu lại
            msg_type = 'HumanMessage' if msg.__class__.__name__ == 'HumanMessage' else 'AIMessage'
            msg_dict = {
                'type': msg_type,
                'content': msg.content,
            }
            serializable_history.append(msg_dict)
        else:
            raise ValueError("Đối tượng không hợp lệ trong history")
    return json.dumps(serializable_history)

def deserialize_history(json_str):
    """
    Chuyển chuỗi JSON (đã được lưu trong cookie) trở lại thành list các đối tượng HumanMessage/AIMessage.
    """
    data = json.loads(json_str)
    history = []

    for item in data:
        msg_type = item.get('type')
        if msg_type == 'HumanMessage':
            # Khởi tạo đối tượng HumanMessage
            msg = HumanMessage(
                content=item['content'],
            )
        elif msg_type == 'AIMessage':
            # Khởi tạo đối tượng AIMessage
            msg = AIMessage(
                content=item['content'],
            )
        else:
            raise ValueError("Loại message không được hỗ trợ")
        history.append(msg)
    return history

def get_cookie_data():
    # Đọc cookie và load vào session_state khi ứng dụng khởi động
    user_info_cookie = get_cookie("user_info")
    id_session_cookie = get_cookie("id_session")

    if user_info_cookie:
        try:
            user_info = json.loads(user_info_cookie)
            st.session_state.user_info = user_info

        except Exception as e:
            st.error(f'Lỗi khi lấy cookie user_info: {e}')

    if id_session_cookie:
        try:
            id_session_dict = json.loads(id_session_cookie)
            st.session_state.id_session_dict = id_session_dict

        except Exception as e:
            st.error(f'Lỗi khi lấy cookie id_session: {e}')

    if st.session_state.get('user_info', {}) and  st.session_state.get('id_session_dict', {}):
        st.session_state.agent_history = get_agent_history_from_firebase(user_info, id_session_dict)
        
    st.session_state.rating_display = True

def delete_all_cookies():
    st_javascript("document.cookie.split(';').forEach(function(c) { "
                  "document.cookie = c.trim().split('=')[0] + '=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/'; });")

def setup_cookie_data():
    try:
        set_cookie(
            name="id_session", 
            value=json.dumps(st.session_state.id_session_dict), 
            duration_days=1/24
        )
        
        set_cookie(
            name="user_info", 
            value=json.dumps(st.session_state.user_info), 
            duration_days=1/24
        )
        
        st.session_state.save_cookie = False

    except Exception as e:
        # Nếu lỗi, xóa hết cookie và chạy lại
        st.warning("Không thể tải dữ liệu session. Đang xóa cookie và tải lại...")
        delete_all_cookies()
        st.session_state.id_session_dict = {
            'log_in_dialog_display': True,
        }
        st.rerun()
