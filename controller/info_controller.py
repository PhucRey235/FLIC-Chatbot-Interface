import streamlit as st
import ast
import random
from datetime import datetime, timezone, timedelta
from google.api_core.exceptions import NotFound
from firebase_admin import firestore  # Cấu hình và truy cập Firestore
import time
from model.database import get_BigQuery_engine

import pathlib
from datetime import datetime

@st.cache_resource(ttl=24*3600, max_entries=1, show_spinner=False)
def get_thong_tin_hoc_vien(phone):
    # Lấy kết nối BigQuery
    Bigquery_db = get_BigQuery_engine()

    # Danh sách cột
    columns = [
        'idHocVien', 'MaSV', 'Ho', 'Ten', 'NgaySinh',
        'GioiTinh', 'DienThoai', 'Email', 'NgayHoc'
    ]
    
    # Truy vấn
    query = f"""
        SELECT {', '.join(columns)}
        FROM HocVien
        WHERE DienThoai = '{phone}'
        LIMIT 1
    """
    
    result = Bigquery_db.run(query)
    
    try:
        result = ast.literal_eval(result)  # Chuyển về list chuẩn
        return dict(zip(columns, result[0]))
        
    # Không phải là Học viên FLIC, trả về rỗng
    except Exception as e:
        return {}
    
def get_thong_tin_quan_ly(phone):   
    if phone == '0123456789':
        thong_tin_quan_ly = {
            'Ho': 'Nguyễn Thành',
            'Ten': 'Thủy',
            'GioiTinh': 'Nam',
            'DienThoai': '0123456789',
        }
        
    else:
        thong_tin_quan_ly = {}
        
    return thong_tin_quan_ly
    
@st.cache_resource(ttl=24*3600, max_entries=1, show_spinner=False)
def khoi_tao_user_info(phone, job, name):
    if job == 'Quản lý':
        thong_tin_quan_ly = get_thong_tin_quan_ly(phone)
        if thong_tin_quan_ly:        
            # Lưu thông tin vào session_state
            user_info = {
                'name': f"{thong_tin_quan_ly.get('Ho', '')} {thong_tin_quan_ly.get('Ten', 'người dùng ẩn danh')}",
                'phone': phone,
                'job': 'Quản lý',
                'la_hoc_vien': False,
                'la_quan_ly': True,
            }

        else:
            # Lưu thông tin vào session_state
            user_info = {
                'name': name,
                'phone': phone,
                'job': job,
                'la_hoc_vien': False,
                'la_quan_ly': False,
            }
    
    else:
        thong_tin_hoc_vien = get_thong_tin_hoc_vien(phone)
    
        if thong_tin_hoc_vien:        
            # Lưu thông tin vào session_state
            user_info = {
                'name': f"{thong_tin_hoc_vien.get('Ho', '')} {thong_tin_hoc_vien.get('Ten', 'người dùng ẩn danh')}",
                'phone': phone,
                'job': 'Học viên FLIC',
                'la_hoc_vien': True,
                'la_quan_ly': False,
            }

        else:
            # Lưu thông tin vào session_state
            user_info = {
                'name': name,
                'phone': phone,
                'job': job,
                'la_hoc_vien': False,
                'la_quan_ly': False,
            }
    st.write(user_info)    
    time.sleep(1000)
    return user_info
        
def transform_cloudinary_url(url, transformation="c_fit,w_300,h_300,ar_1:1,q_auto,f_auto"):
    if "res.cloudinary.com" in url and "/upload/" in url:
        return url.replace("/upload/", f"/upload/{transformation}/")
    return url  # không thay đổi nếu không phải ảnh Cloudinary
        
def display_likert_image(category: str = 'nghiem_tuc'):
    # Danh sách ảnh thang đo likert chia theo loại và số sao
    likert_images = {
        "hai": {
            1: [
                "https://res.cloudinary.com/day4wv1aw/image/upload/v1746102781/flic_chatbot/emoji/H%C3%A0i/1_om6dhw.jpg",
                "https://res.cloudinary.com/day4wv1aw/image/upload/v1746104355/flic_chatbot/emoji/H%C3%A0i/1_pgwucr.jpg",
            ],
            2: [
                "https://res.cloudinary.com/day4wv1aw/image/upload/v1746102781/flic_chatbot/emoji/H%C3%A0i/2_jm91m9.jpg",
                "https://res.cloudinary.com/day4wv1aw/image/upload/v1746102781/flic_chatbot/emoji/H%C3%A0i/2_2_ftju3h.jpg",
            ],
            3: [
                "https://res.cloudinary.com/day4wv1aw/image/upload/v1746102781/flic_chatbot/emoji/H%C3%A0i/3_ohktap.jpg",
                "https://res.cloudinary.com/day4wv1aw/image/upload/v1746102781/flic_chatbot/emoji/H%C3%A0i/3_ohktap.jpg",
            ],
            4: [
                "https://res.cloudinary.com/day4wv1aw/image/upload/v1746102781/flic_chatbot/emoji/H%C3%A0i/4_w0j80f.jpg",
                "https://res.cloudinary.com/day4wv1aw/image/upload/v1746104454/flic_chatbot/emoji/H%C3%A0i/4_snba93.jpg",
            ],
            5: [
                "https://res.cloudinary.com/day4wv1aw/image/upload/v1746102781/flic_chatbot/emoji/H%C3%A0i/5_mlarol.jpg",
                "https://res.cloudinary.com/day4wv1aw/image/upload/v1746102782/flic_chatbot/emoji/H%C3%A0i/5_cbawbc.png",
            ],
        },
        "nghiem_tuc": {
            1: [
                "https://res.cloudinary.com/day4wv1aw/image/upload/v1746112679/flic_chatbot/emoji/Nghi%C3%AAm%20t%C3%BAc/1_1_mm3jqg.png",
            ],
            2: [
                "https://res.cloudinary.com/day4wv1aw/image/upload/v1746112678/flic_chatbot/emoji/Nghi%C3%AAm%20t%C3%BAc/2_p1vsbn.png"
            ],
            3: [
                "https://res.cloudinary.com/day4wv1aw/image/upload/v1746112680/flic_chatbot/emoji/Nghi%C3%AAm%20t%C3%BAc/3_ivsjqk.png",
            ],
            4: [
                "https://res.cloudinary.com/day4wv1aw/image/upload/v1746112678/flic_chatbot/emoji/Nghi%C3%AAm%20t%C3%BAc/4_kbhkdg.png"
            ],
            5: [    
                "https://res.cloudinary.com/day4wv1aw/image/upload/v1746112679/flic_chatbot/emoji/Nghi%C3%AAm%20t%C3%BAc/5_mtmbx8.png",
            ],
        }
    }
    
    category_key = category.lower()
    
    if category_key not in likert_images:
        st.error("Loại không hợp lệ. Chọn 'loai1' hoặc 'loai2'.")
        return
        
    star = st.session_state.selected_feedback_dialog + 1 
    
    if star not in likert_images[category_key]:
        st.error("Không có ảnh cho số sao này.") 
        return

    image_url = random.choice(likert_images[category_key][star])
    transformed_url = transform_cloudinary_url(image_url)
    
    st.markdown(
        f"""
        <style>
            .centered {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
            }}
        </style>
        <div class="centered">
            <img src="{transformed_url}" height="150px">
        </div>
        """,
        unsafe_allow_html=True
    )        
    
def save_feedback(feedback_type, feedback_content):
    current_time = datetime.now(timezone.utc).isoformat()
    feedbacks_ref = st.session_state.firebase_db.collection("feedbacks").document(st.session_state.get('id_session_dict', {}).get('userID', ''))
    
    feedback_data = {
        "feedbackType": feedback_type,
        "content": feedback_content,
        "rating": st.session_state.selected_feedback_dialog + 1,  # giả sử bạn dùng session_state lưu số sao
        "summitAt": current_time,  # hoặc current_time nếu bạn đã có
    }

    try:
        # Dùng ArrayUnion để thêm feedback mới vào mảng feedbacks
        feedbacks_ref.update({
            "feedbacks": firestore.ArrayUnion([feedback_data])
        })

    except NotFound:
        # Nếu document chưa tồn tại, tạo mới và thêm feedback
        feedbacks_ref.set({
            "feedbackID": st.session_state.get('id_session_dict', {}).get('userID', ''),
            "feedbacks": [feedback_data],
            "metadata": {
                "conversationID": st.session_state.get('id_session_dict', {}).get('conversationID', ''),
                "userName": st.session_state.get('user_info', {}).get('name', ''),
                "job": st.session_state.get('user_info', {}).get('job', ''),
                "phone": st.session_state.get('user_info', {}).get('phone', ''),
                "platform": "RAG",
            }
        }, merge=True)

def save_yeu_cau_nhan_vien(loi_nhan_tu_dong):
    """
    Lưu tin nhắn vào Firebase Firestore và cập nhật thông tin userchats sử dụng batch.
    """
    current_time = datetime.now(timezone.utc).isoformat()
    
    # Tham chiếu đến các document
    users_ref = st.session_state.firebase_db.collection("users").document(st.session_state.get('id_session_dict', {}).get('userID', '')) 
    chat_list_ref = st.session_state.firebase_db.collection("chatList").document(st.session_state.get('id_session_dict', {}).get('conversationID', ''))
    chat_content_ref = st.session_state.firebase_db.collection("chatContent").document(st.session_state.get('id_session_dict', {}).get('conversationID', ''))
    
    bot_message = {
        "messageID": f"MSG{len(st.session_state.agent_history):03d}",
        "sender": {
            "type": "chatbotRAG", # user, employee, system, bot
            "id": st.session_state.get('id_session_dict', {}).get('botID', '')
        },
        "content": {
            "text": loi_nhan_tu_dong,
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
        "response_usage": ''
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
            "lastMessage": loi_nhan_tu_dong,
            "lastUpdated": current_time,
            "unreadCount": firestore.Increment(1),  # Tăng giá trị hiện tại lên 1 
            "requestEmployee": True,

        })
        
        # Thêm tin nhắn mới vào chatContent
        batch.update(chat_content_ref, {
            "messages": firestore.ArrayUnion([bot_message])
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
            "lastMessage": loi_nhan_tu_dong,
            "lastUpdated": current_time,
            "status": "active",
            "unreadCount": 1,
            "requestEmployee": True,
        }, merge=True)
        
        # Tạo document trong chatContent với hai tin nhắn đầu tiên
        batch.set(chat_content_ref, {
            "conversationID": st.session_state.get('id_session_dict', {}).get('conversationID', ''),
            "messages": [bot_message]
        }, merge=True)
              
        # Thực hiện batch
        batch.commit()
        return 
    
def save_tat_yeu_cau_nhan_vien():
    """
    Lưu tin nhắn vào Firebase Firestore và cập nhật thông tin userchats sử dụng batch.
    """
    current_time = datetime.now(timezone.utc).isoformat()
    
    # Tham chiếu đến các document
    chat_list_ref = st.session_state.firebase_db.collection("chatList").document(st.session_state.get('id_session_dict', {}).get('conversationID', ''))
    
    try:
        # Nếu đã tồn tại, cập nhật chatList
        chat_list_ref.update({
            "requestEmployee": False,
        })
        
        return 
        
    except NotFound:
        # Nếu chưa tồn tại, tạo mới document trong chatList
        chat_list_ref.set({
            "conversationID": st.session_state.get('id_session_dict', {}).get('conversationID', ''),
            "userID": st.session_state.get('id_session_dict', {}).get('userID', ''),
            "name": st.session_state.get('user_info', {}).get('name', ''),
            "avatar": None,
            "platforms": "RAG",
            "lastMessage": '',
            "lastUpdated": current_time,
            "status": "active",
            "unreadCount": 1,
            "requestEmployee": False,
        }, merge=True)
        
        return 
    