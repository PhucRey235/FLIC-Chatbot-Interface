import streamlit as st  # Dùng để hiển thị lỗi và cache resource
from datetime import datetime, timezone, timedelta
from google.api_core.exceptions import NotFound
from firebase_admin import firestore  # Cấu hình và truy cập Firestore

def save_welcome_message_to_firebase(welcome_message, id_session_dict, user_info, agent_history):
    current_time = (datetime.now(timezone.utc)
    
    # Tham chiếu đến các document
    users_ref = st.session_state.firebase_db.collection("users").document(id_session_dict.get('userID', '')) 
    chat_list_ref = st.session_state.firebase_db.collection("chatList").document(id_session_dict.get('conversationID', ''))
    chat_content_ref = st.session_state.firebase_db.collection("chatContent").document(id_session_dict.get('conversationID', ''))

    bot_welcome = {
        "messageID": f"MSG{len(agent_history)-2:03d}",
        "sender": {
            "type": "chatbotRAG", # user, employee, system, bot
            "id": id_session_dict.get('botID', '')
        },
        "content": {
            "text": welcome_message,
            "type": "text", # text, image, file, video, audio, location
            "attachments": [],
        "timestamp": current_time,
        },
        "status": {
            "sendAt": current_time,
            "readBy": None,
            "readAt": None,
            "response_time": None,
        },
    }
    
    # Tạo batch để thực hiện tất cả các thao tác trong một lần gửi
    batch = st.session_state.firebase_db.batch()
    
    # Tạo document mới với cả hai tin nhắn
    batch.set(users_ref, {
        "userID": id_session_dict.get('userID', ''),
        "platforms": {
            "type": "RAG",
            "id": id_session_dict.get('userID', ''),
            "name": user_info.get('name', ''),
            "conversationID": id_session_dict.get('conversationID', ''),
            "firstInteraction": current_time
        },
        "contactInfo": {
            "phone": user_info.get('phone', ''),
            "name": user_info.get('name', ''),
            "job": user_info.get('job', ''),
        },
        "metadata": {
            "createdAt": current_time,
            "totalConversations": len(agent_history),
            "lastUpdated": current_time,
        }
    }, merge=True)  # Sử dụng merge=True để không ghi đè dữ liệu hiện có
    
    # Nếu chưa tồn tại, tạo mới document trong chatList
    batch.set(chat_list_ref, {
        "conversationID": id_session_dict.get('conversationID', ''),
        "userID": id_session_dict.get('userID', ''),
        "name": user_info.get('name', ''),
        "avatar": None,
        "platforms": "RAG",
        "lastMessage": welcome_message,
        "lastUpdated": current_time,
        "status": "active",
        "unreadCount": 1,
        "requestEmployee": False,
    })
    
    # Tạo document trong chatContent với hai tin nhắn đầu tiên
    batch.set(chat_content_ref, {
        "conversationID": id_session_dict.get('conversationID', ''),
        "messages": [bot_welcome]
    })
                
    # Thực hiện batch
    batch.commit()
    
    return 

def save_message_to_firebase(response, response_usage, user_input):
    """
    Lưu tin nhắn vào Firebase Firestore và cập nhật thông tin userchats sử dụng batch.
    """
    current_time = (datetime.now(timezone.utc)
    
    # Tham chiếu đến các document
    users_ref = st.session_state.firebase_db.collection("users").document(st.session_state.get('id_session_dict', {}).get('userID', '')) 
    chat_list_ref = st.session_state.firebase_db.collection("chatList").document(st.session_state.get('id_session_dict', {}).get('conversationID', ''))
    chat_content_ref = st.session_state.firebase_db.collection("chatContent").document(st.session_state.get('id_session_dict', {}).get('conversationID', ''))
        
    user_message = {
        "messageID": f"MSG{len(st.session_state.agent_history)-1:03d}",
        "sender": {
            "type": "user", # user, employee, system, bot
            "id": st.session_state.get('id_session_dict', {}).get('userID', '')
        },
        "content": {
            "text": user_input,
            "type": "text", # text, image, file, video, audio, location
            "attachments": [],
        "timestamp": current_time,
        },
        "status": {
            "sendAt": current_time,
            "readBy": None,
            "readAt": None,
            "response_time": None,
        },
    }
    
    bot_message = {
        "messageID": f"MSG{len(st.session_state.agent_history):03d}",
        "sender": {
            "type": "chatbotRAG", # user, employee, system, bot
            "id": st.session_state.get('id_session_dict', {}).get('botID', '')
        },
        "content": {
            "text": response,
            "type": "text", # text, image, file, video, audio, location
            "attachments": [],
        "timestamp": current_time,
        },
        "status": {
            "sendAt": current_time,
            "readBy": None,
            "readAt": None,
            "response_time": None,
        },
        "response_usage": response_usage
    }

    try:
        # Tạo batch để thực hiện tất cả các thao tác trong một lần gửi
        batch = st.session_state.firebase_db.batch()
    
        # Thử cập nhật các documents
        # Luôn sử dụng set cho users_ref để tránh lỗi khi document không tồn tại
        batch.set(users_ref, {
            "metadata": {
                "totalConversations": len(st.session_state.agent_history),
                "lastUpdated": current_time,
            },
            "contactInfo": {
                "job": st.session_state.user_info.get('job', ''),
            }
        }, merge=True)
        
        # Nếu đã tồn tại, cập nhật chatList
        batch.update(chat_list_ref, {
            "lastMessage": response,
            "lastUpdated": current_time,
            "unreadCount": firestore.Increment(1)  # Tăng giá trị hiện tại lên 1 
        })
        
        # Thêm tin nhắn mới vào chatContent
        batch.update(chat_content_ref, {
            "messages": firestore.ArrayUnion([user_message, bot_message])
        })
        
        # Thực hiện batch
        batch.commit()
        return 
        
    except NotFound:
        st.warning("Không tìm thấy tài liệu, tạo mới...")
        # Tạo batch để thực hiện tất cả các thao tác trong một lần gửi
        batch = st.session_state.firebase_db.batch()
        
        # Tạo document mới với cả hai tin nhắn
        batch.set(users_ref, {
            "userID": st.session_state.get('id_session_dict', {}).get('userID', ''),
            "platforms": {
                "name": "RAG",
                "id": st.session_state.get('id_session_dict', {}).get('userID', ''),
                "name": st.session_state.get('user_info', {}).get('name', ''),
                "conversationID": st.session_state.get('id_session_dict', {}).get('conversationID', ''),
                "firstInteraction": current_time
            },
            "contactInfo": {
                "phone": st.session_state.get('user_info', {}).get('phone', ''),
                "name": st.session_state.get('user_info', {}).get('name', ''),
                "job": st.session_state.get('user_info', {}).get('job', ''),
            },
            "metadata": {
                "createdAt": current_time,
                "totalConversations": len(st.session_state.agent_history),
                "lastUpdated": current_time,
            }
        }, merge=True)  # Sử dụng merge=True để không ghi đè dữ liệu hiện có
        
        # Nếu chưa tồn tại, tạo mới document trong chatList
        batch.set(chat_list_ref, {
            "conversationID": st.session_state.get('id_session_dict', {}).get('conversationID', ''),
            "userID": st.session_state.get('id_session_dict', {}).get('userID', ''),
            "name": st.session_state.get('user_info', {}).get('name', ''),
            "avatar": None,
            "platforms": "RAG",
            "lastMessage": response,
            "lastUpdated": current_time,
            "status": "active",
            "unreadCount": 1,
            "requestEmployee": False,
        })
        
        # Tạo document trong chatContent với hai tin nhắn đầu tiên
        batch.set(chat_content_ref, {
            "conversationID": st.session_state.get('id_session_dict', {}).get('conversationID', ''),
            "messages": [user_message, bot_message]
        })
              
        # Thực hiện batch
        batch.commit()
        return 
    
def save_message_to_firebase_with_employee(user_input):
    """
    Lưu tin nhắn vào Firebase Firestore và cập nhật thông tin userchats sử dụng batch.
    """
    current_time = (datetime.now(timezone.utc)
    
    # Tham chiếu đến các document
    users_ref = st.session_state.firebase_db.collection("users").document(st.session_state.get('id_session_dict', {}).get('userID', '')) 
    chat_list_ref = st.session_state.firebase_db.collection("chatList").document(st.session_state.get('id_session_dict', {}).get('conversationID', ''))
    chat_content_ref = st.session_state.firebase_db.collection("chatContent").document(st.session_state.get('id_session_dict', {}).get('conversationID', ''))
        
    user_message = {
        "messageID": f"MSG{len(st.session_state.agent_history)-1:03d}",
        "sender": {
            "type": "user", # user, employee, system, bot
            "id": st.session_state.get('id_session_dict', {}).get('userID', '')
        },
        "content": {
            "text": user_input,
            "type": "text", # text, image, file, video, audio, location
            "attachments": [],
        "timestamp": current_time,
        },
        "status": {
            "sendAt": current_time,
            "readBy": None,
            "readAt": None,
            "response_time": None,
        },
    }

    try:
        # Tạo batch để thực hiện tất cả các thao tác trong một lần gửi
        batch = st.session_state.firebase_db.batch()
    
        # Thử cập nhật các documents
        # Luôn sử dụng set cho users_ref để tránh lỗi khi document không tồn tại
        batch.set(users_ref, {
            "metadata": {
                "totalConversations": len(st.session_state.agent_history),
                "lastUpdated": current_time,
            },
            "contactInfo": {
                "job": st.session_state.user_info.get('job', ''),
            }
        }, merge=True)
        
        # Nếu đã tồn tại, cập nhật chatList
        batch.update(chat_list_ref, {
            "lastMessage": user_input,
            "lastUpdated": current_time,
            "unreadCount": firestore.Increment(1),  # Tăng giá trị hiện tại lên 1 
            "requestEmployee": True,
        })
        
        # Thêm tin nhắn mới vào chatContent
        batch.update(chat_content_ref, {
            "messages": firestore.ArrayUnion([user_message])
        })
        
        # Thực hiện batch
        batch.commit()
        return 
        
    except NotFound:
        st.warning("Không tìm thấy tài liệu, tạo mới...")
        # Tạo batch để thực hiện tất cả các thao tác trong một lần gửi
        batch = st.session_state.firebase_db.batch()
        
        # Tạo document mới với cả hai tin nhắn
        batch.set(users_ref, {
            "userID": st.session_state.get('id_session_dict', {}).get('userID', ''),
            "platforms": {
                "name": "RAG",
                "id": st.session_state.get('id_session_dict', {}).get('userID', ''),
                "name": st.session_state.get('user_info', {}).get('name', ''),
                "conversationID": st.session_state.get('id_session_dict', {}).get('conversationID', ''),
                "firstInteraction": current_time
            },
            "contactInfo": {
                "phone": st.session_state.get('user_info', {}).get('phone', ''),
                "name": st.session_state.get('user_info', {}).get('name', ''),
                "job": st.session_state.get('user_info', {}).get('job', ''),
            },
            "metadata": {
                "createdAt": current_time,
                "totalConversations": len(st.session_state.agent_history),
                "lastUpdated": current_time,
            }
        }, merge=True)  # Sử dụng merge=True để không ghi đè dữ liệu hiện có
        
        # Nếu chưa tồn tại, tạo mới document trong chatList
        batch.set(chat_list_ref, {
            "conversationID": st.session_state.get('id_session_dict', {}).get('conversationID', ''),
            "userID": st.session_state.get('id_session_dict', {}).get('userID', ''),
            "name": st.session_state.get('user_info', {}).get('name', ''),
            "avatar": None,
            "platforms": "RAG",
            "lastMessage": user_input,
            "lastUpdated": current_time,
            "status": "active",
            "unreadCount": 1,
            "requestEmployee": True,
        })
        
        # Tạo document trong chatContent với hai tin nhắn đầu tiên
        batch.set(chat_content_ref, {
            "conversationID": st.session_state.get('id_session_dict', {}).get('conversationID', ''),
            "messages": [user_message]
        })
              
        # Thực hiện batch
        batch.commit()
        return 