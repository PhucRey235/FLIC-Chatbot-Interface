# controller/chat_controller.py
import streamlit as st  # Dùng để hiển thị giao diện và xử lý input
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, AIMessageChunk, ToolMessage  # Định dạng tin nhắn
import time  # Tạo hiệu ứng gõ chữ

from .message_controller import save_message_to_firebase, save_message_to_firebase_with_employee  # Import hàm lưu tin nhắn

from .on_snapshot_controller import reset_interact_interface
from .message_controller import save_welcome_message_to_firebase

def handle_user_input():
    # if st.session_state.get('agent_history', '') != '':
    #     raise ValueError("agent_history chưa được khởi tạo")  # Kiểm tra nếu agent_executor là None
    
    # if st.session_state.get('agent_executor', '') != '':
    #     raise ValueError("agent_executor chưa được khởi tạo")  # Kiểm tra nếu agent_executor là None
    
    # if st.session_state.get('id_session_dict', {}).get('userID', '') != '':
    #     raise ValueError("userID chưa được khởi tạo")  # Kiểm tra nếu agent_executor là None
    
    # if st.session_state.get('id_session_dict', {}).get('botID', '') != '':
    #     raise ValueError("botID chưa được khởi tạo")  # Kiểm tra nếu agent_executor là None
    
    # if st.session_state.get('id_session_dict', {}).get('conversationID', '') != '':
    #     raise ValueError("conversationID chưa được khởi tạo")  # Kiểm tra nếu agent_executor là None
    
    # if st.session_state.get('firebase_db', '') != '':
    #     raise ValueError("firebase_db chưa được khởi tạo")  # Kiểm tra nếu agent_executor là None
    
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
        # Đánh dấu là đang xử lý
        if st.session_state.get('user_info', {}).get('phone', '') == '':
            st.warning("Vui lòng nhập thông tin người dùng trước khi đặt câu hỏi.")
            return

        # Sau khi người dùng gửi tin nhắn mới hiển thị lại số sao mới
        st.session_state.rating_display = True
        
        # Thêm tin nhắn người dùng vào lịch sử
        st.session_state.agent_history.append(HumanMessage(content=user_input))
        
        # Hiển thị tin nhắn người dùng (xử lý xuống dòng)
        message_xuong_dong = user_input.replace("\n", "  \n")
        st.chat_message("human").markdown(message_xuong_dong)

        with st.spinner("Vui lòng chờ trong giây lát..."):  # Hiển thị spinner khi xử lý
            start_time = time.time()
            
            # Chuẩn bị tin nhắn gửi cho agent
            summarized_message = [SystemMessage(content=st.session_state.customized_prompt)]
            summarized_message.extend(st.session_state.agent_history)
            st.write(st.session_state.customized_prompt)
            # Gọi agent để lấy phản hồi
            output = st.session_state.agent_executor.invoke({"messages": summarized_message})
            response = output["messages"][-1].content  # Lấy phản hồi cuối cùng
            response_usage = output["messages"][-1].usage_metadata
            
            st.session_state.agent_history.append(AIMessage(
                content=response, 
            ))
            
            # Lưu tin nhắn bot vào Firebase
            save_message_to_firebase(response, response_usage, user_input)
            
            with st.chat_message("assistant"):
                messages_split = response.split(' ')

                full_response = ""
                text_container = st.markdown("")
                
                for word in messages_split:
                    full_response += word + " "
                    text_container.markdown(full_response)
                    time.sleep(0.005)  # Delay 0.02 giây giữa các từ
                        
            st.rerun()

def handle_user_input_with_employee():
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
        # Đánh dấu là đang xử lý
        if st.session_state.get('user_info', {}).get('phone', '') == '':
            st.warning("Vui lòng nhập thông tin người dùng trước khi đặt câu hỏi.")
            return

        # Sau khi người dùng gửi tin nhắn mới hiển thị lại số sao mới
        st.session_state.rating_display = True
        
        # Hiển thị tin nhắn người dùng (xử lý xuống dòng)
        message_xuong_dong = user_input.replace("\n", "  \n")
        st.chat_message("human").markdown(message_xuong_dong)
        
        # Thêm tin nhắn người dùng vào lịch sử
        st.session_state.agent_history.append(HumanMessage(content=user_input))

        save_message_to_firebase_with_employee(user_input)
        reset_interact_interface()

def get_agent_history_from_firebase(user_info, id_session_dict):
    # Kiểm tra xem số điện thoại có tồn tại người dùng không
    # Nếu không thì lấy tên người dùng điền để dùng và tạo người dùng mới
    doc_ref = st.session_state.firebase_db.collection("chatContent").document(f"RAG{user_info.get('phone','')}")
    
    doc = doc_ref.get()
    
    if doc.exists:
        data = doc.to_dict().get("messages", [])
        agent_history = []

        for message in data:
            sender_type = message.get("sender", {}).get("type", "")
            text = message.get("content", {}).get("text", "")
            
            if sender_type == "user":
                agent_history.append(HumanMessage(content=text))
            else:
                agent_history.append(AIMessage(content=text))

                                
    # Cá nhân hóa người dùng khi chào bằng tên            
    else:
        welcome_message = f"Tôi có thể giúp gì cho bạn {user_info.get('name', 'người dùng ẩn danh')}?"
        # Khởi tạo với lời chào mặc định của bot
        agent_history = [
            AIMessage(content=welcome_message)
        ]
        
        save_welcome_message_to_firebase(welcome_message, id_session_dict, user_info, agent_history)
        
    return agent_history