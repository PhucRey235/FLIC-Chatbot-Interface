# view/interface.py
import streamlit as st  # Dùng để tạo giao diện

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, AIMessageChunk, ToolMessage  # Định dạng tin nhắn

from controller.info_controller import save_yeu_cau_nhan_vien

from .dialog import setup_feedback_dialog

def setup_page():
    """
    Cấu hình trang web cơ bản:
    - Đặt tiêu đề trang, icon và layout (wide).
    """
    st.set_page_config(
        page_title="FLIC Chatbot",   # Tiêu đề hiển thị trên tab trình duyệt
        page_icon="https://res.cloudinary.com/day4wv1aw/image/upload/v1741313942/flic_chatbot/OIP-removebg-preview_vrvzha.png", # Icon trên tab
        layout="centered", # Giao diện rộng
        initial_sidebar_state="auto" # ("auto", "expanded", or "collapsed")
    )

def setup_sidebar():
    st.sidebar.markdown(
        """
        <div style="display: flex; justify-content: center;">
            <img src="https://res.cloudinary.com/day4wv1aw/image/upload/v1741313942/flic_chatbot/OIP-removebg-preview_vrvzha.png" 
            width="150">
        </div>
        """, 
        unsafe_allow_html=True
    )

    # Thêm CSS tùy chỉnh để căn giữa tiêu đề trong sidebar
    st.markdown(
        """
        <style>
            /* Căn giữa tiêu đề trong sidebar */
            [data-testid="stHeading"] {
                text-align: center;
            }
            
            /* Xóa khoảng trống trên cùng cho sidebar */
            [data-testid="stSidebarHeader"] {
                height: 50px;  /* Giảm chiều cao */
                padding: 20px;  /* Xóa padding để thu gọn hơn */
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.subheader("")
    # Tạo tiêu đề trong sidebar
    st.sidebar.header("GIỚI THIỆU")
    
    st.sidebar.markdown(
        'FLIC (Trung tâm Ngoại ngữ - Tin học), trực thuộc Trường Đại học Kinh tế Đà Nẵng, '
        'có nhiệm vụ cung cấp dịch vụ đào tạo và đánh giá năng lực ngoại ngữ, công nghệ thông tin cho sinh viên.'
    )
    st.sidebar.subheader("")
    st.sidebar.subheader("")
    st.sidebar.header("THÔNG TIN LIÊN HỆ")

    # HTML và CSS để hiển thị icon trên một hàng
    st.sidebar.markdown("""
        <style>
            .icon-container {
                display: flex;
                justify-content: center;
                gap: 20px;
            }
            .icon-container a img {
                width: 40px;
                height: 40px;
            }
        </style>
        <div class="icon-container">
            <a href="https://maps.app.goo.gl/SNVJgcejAN1hF2p68" target="_blank">
                <img src="https://res.cloudinary.com/day4wv1aw/image/upload/v1741413156/flic_chatbot/Marker_w6ugns.png">
            </a>
            <a href="https://zalo.me/84901951616" target="_blank">
                <img src="https://res.cloudinary.com/day4wv1aw/image/upload/v1741535249/flic_chatbot/Zalo_jjbd9c.png">
            </a>
            <a href="https://flic.due.udn.vn/" target="_blank">
                <img src="https://res.cloudinary.com/day4wv1aw/image/upload/v1741413155/flic_chatbot/Globe_czih80.png">
            </a>
            <a href="https://www.facebook.com/FLIC.DUE.UDN.VN" target="_blank">
                <img src="https://res.cloudinary.com/day4wv1aw/image/upload/v1741412988/flic_chatbot/Facebook_owyz2s.png">
            </a>
        </div>
    """, unsafe_allow_html=True)

def setup_introduction():
    """
    Thiết lập giao diện chat chính:
    - Hiển thị tiêu đề, caption và lịch sử chat.
    """
    
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
            <h1>FLIC Chatbot</h1>
            <p style="font-size: 16px; color: gray; max-width: 450px;">
                Giúp bạn giải đáp mọi thắc mắc về khóa học, lịch học, học phí và nhiều thông tin khác một cách nhanh chóng, chính xác
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
def setup_chat_interface():
    """
    Thiết lập giao diện chat chính:
    - Hiển thị tin nhắn của bot và người dùng theo định dạng thích hợp.
    """
    if "display_history" not in st.session_state:
        st.session_state.display_history = False
    
    # Giả sử num_messages_display được định nghĩa trước đó
    num_messages_display = 10

    # Thay thế nội dung rỗng trong st.session_state.agent_history
    for msg in st.session_state.agent_history:
        if hasattr(msg, 'content') and not msg.content.strip():
            msg.content = "rỗng"

    # Nếu lịch sử nhiều hơn num_messages_display tin và chưa bật chế độ hiển thị đầy đủ,
    # ban đầu chỉ hiển thị num_messages_display tin nhắn cuối.
    if len(st.session_state.agent_history) > num_messages_display and not st.session_state.display_history:
        display_history_data = st.session_state.agent_history[-num_messages_display:]
        
        # Hiển thị nút "Xem thêm lịch sử" nếu chưa hiển thị toàn bộ lịch sử
        if st.button("Xem thêm lịch sử"):
            st.session_state.display_history = True
            st.rerun()
            
    else:
        display_history_data = st.session_state.agent_history


    last_ai_message_index = -1
    if display_history_data: # Đảm bảo danh sách không trống
        # Duyệt ngược từ cuối danh sách để tìm AIMessage đầu tiên (chính là AIMessage cuối cùng)
        for i in range(len(display_history_data) - 1, -1, -1):
            if isinstance(display_history_data[i], AIMessage):
                last_ai_message_index = i
                break # Đã tìm thấy, thoát vòng lặp

    if 'rating_display' not in st.session_state:
        st.session_state.rating_display = True
        
    # Hiển thị lịch sử chat theo định dạng của streamlit chat message
    for i, msg in enumerate(display_history_data): # Sử dụng enumerate để lấy cả index
        # Kiểm tra nội dung tin nhắn, bỏ qua nếu content là "rỗng"
        if hasattr(msg, 'content') and msg.content == "rỗng":
            continue
        
        if isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)

            # Kiểm tra xem đây có phải là tin nhắn AIMessage cuối cùng không
            # VÀ các điều kiện hiển thị rating có đúng không
            if i == last_ai_message_index \
            and len(st.session_state.agent_history) > 1 \
            and st.session_state.get('rating_display', False):
                col1, col2 = st.columns([1,1])
                
                with col1:
                    rating = st.feedback(options = "stars", key = 'feedback_rating_setup_interface')
                    
                    if rating is not None:
                        st.session_state.selected_feedback_dialog = rating
                        st.session_state.feedback_log_in_dialog_display = True  # Bật hiển thị dialog
                    
                with col2:        
                    if st.button("Gặp nhân viên", key = 'button_setup_interface'):
                        loi_nhan_tu_dong = 'Cảm ơn bạn đã để lại yêu cầu. Hệ thống đã ghi nhận và sẽ chuyển tiếp đến nhân viên hỗ trợ trong thời gian sớm nhất. Thời gian làm việc của nhân viên là từ Thứ Hai đến Thứ Sáu, 7h đến 11h và 13h đến 17h. Rất mong bạn thông cảm nếu phản hồi có thể chậm ngoài khung giờ này.'
                        st.session_state.agent_history.append(AIMessage(content=loi_nhan_tu_dong))
                        
                        save_yeu_cau_nhan_vien(loi_nhan_tu_dong)
                        st.chat_message('assistant').markdown(loi_nhan_tu_dong)
                        
                        # Khởi tạo session_state cho listener và timer nếu chưa tồn tại
                        if 'listener' not in st.session_state:
                            st.session_state.listener = None
                        if 'idle_timer' not in st.session_state:
                            st.session_state.idle_timer = None
                        
                        st.session_state.gap_nhan_vien = True
                        st.rerun()

        elif isinstance(msg, HumanMessage):
            # Hiển thị tin nhắn người dùng như bình thường
            message_xuong_dong = msg.content.replace("\n", "  \n")
            st.chat_message("human").markdown(message_xuong_dong)
            
    if st.session_state.get('feedback_log_in_dialog_display', False):
        setup_feedback_dialog()

    return st.session_state.agent_history

def setup_chat_interface_with_employee():
    """
    Thiết lập giao diện chat chính:
    - Hiển thị tin nhắn của bot và người dùng theo định dạng thích hợp.
    """
    if "display_history" not in st.session_state:
        st.session_state.display_history = False
    
    # Giả sử num_messages_display được định nghĩa trước đó
    num_messages_display = 10

    # Nếu lịch sử nhiều hơn num_messages_display tin và chưa bật chế độ hiển thị đầy đủ,
    # ban đầu chỉ hiển thị num_messages_display tin nhắn cuối.
    if len(st.session_state.agent_history) > num_messages_display and not st.session_state.display_history:
        display_history_data = st.session_state.agent_history[-num_messages_display:]
        
        # Hiển thị nút "Xem thêm lịch sử" nếu chưa hiển thị toàn bộ lịch sử
        if st.button("Xem thêm lịch sử"):
            st.session_state.display_history = True
            st.rerun()
            
    else:
        display_history_data = st.session_state.agent_history

    # Hiển thị lịch sử chat theo định dạng của streamlit chat message
    for msg in display_history_data: # Sử dụng enumerate để lấy cả index
        if isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)

        elif isinstance(msg, HumanMessage):
            # Hiển thị tin nhắn người dùng như bình thường
            message_xuong_dong = msg.content.replace("\n", "  \n")
            st.chat_message("human").markdown(message_xuong_dong)
    


    return st.session_state.agent_history


