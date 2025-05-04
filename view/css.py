# view/css.py
import streamlit as st  # Dùng để chèn CSS vào giao diện

# Điều chỉnh lại các css cho đẹp
def load_custom_css():
    st.markdown(
        """
        <style>
            /* Tạo màu gradient cho nền chính */
            /* Gradient nền chính */
            [data-testid="stApp"] {
                background-color: #f2f0ef;
                background: linear-gradient(to bottom right, #B0EAF5, #F2EFF1, #F9D7C0);
                background-attachment: fixed;
                background-size: cover;
            }
            /* Xóa màu trắng trên các phần tử con */
            [data-testid="stBottom"] > * { 
                background-color: transparent !important;
            }
            [data-testid="stHeader"]
            {
                background-color: transparent !important;
            }
            /* Áp dụng gradient cho stBottom để đồng bộ với nền chính */
            [data-testid="stBottom"] {
                background: linear-gradient(to bottom right, #B0EAF5, #F2EFF1, #F9D7C0);
                background-attachment: fixed;
                background-size: cover;
            }    
            
            /* Loại bỏ khoảng trắng ở trên của nền chính */
            [data-testid="stMainBlockContainer"] {
                padding-top: 2rem !important;
            }

            /* Tạo màu gradient cho sidebar */
            [data-testid="stSidebar"] {
            background: linear-gradient(to top, #E1F5FE, #FFFFFF);
            color: #333333; /* Màu nâu đậm */
            }
        
            /* Chuyển tin nhắn về phía bên phải và xóa hình ava và điều chỉnh khung chat */
            /* Chỉ chọn những phần tử [data-testid="stChatMessage"] mà bên trong có [data-testid="stChatMessageAvatarUser"] */
            [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
                background-color: #eff6ff; /* Màu nền */
                color: #333; /* Màu chữ xám đậm */
                border-radius: 16px; /* Góc bo tròn */
                padding: 14px; /* Khoảng đệm */
                margin-bottom: 10px; /* Lề dưới */
                margin-top: 10px; /* Lề trên */
                display: inline-block !important; /* Cho phép tự động thu nhỏ theo nội dung */
                max-width: 80%; /* Giới hạn chiều rộng */
                text-align: left ; /* Căn lề trái */
                width: fit-content; /* Đảm bảo ô chat thu nhỏ khi nội dung ít */
                word-wrap: break-word ; /* Ngắt dòng */
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); /* Thêm hiệu ứng bóng đổ */
                margin-left: auto ; /* Đẩy tin nhắn về bên phải */
                margin-right: 0px ; /* Loại bỏ margin bên phải */
            }
            
            /* Ẩn đi avatar của user */  
            [data-testid="stChatMessageAvatarUser"] {
                position: absolute !important; 
                width: 0 !important;
                height: 0 !important;
                overflow: hidden !important;
                opacity: 0 !important;
                pointer-events: none !important;
            }
            /* Áp dụng CSS cho tất cả các phần tử con bên trong để chuyển chữ sang phải và giữ màu */
            [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) * {
                color: inherit !important; /* Kế thừa màu chữ */
                display: inline !important; /* Đảm bảo tin nhắn không mở rộng quá mức */
            }
            
            /* Chuyển tin nhắn về phía bên trái và xóa hình ava và điều chỉnh khung chat */
            /* Chỉ chọn những phần tử [data-testid="stChatMessage"] mà bên trong có [data-testid="stChatMessageAvatarAssistant"] */
            [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
                background-color: #FBF8FB; /* Màu nền */
                color: #333; /* Màu chữ xám đậm */
                border-radius: 16px; /* Góc bo tròn */
                padding: 14px; /* Khoảng đệm */
                margin-bottom: 10px; /* Lề dưới */
                margin-top: 10px; /* Lề trên */
                display: flex;
                width: fit-content; /* Đảm bảo ô chat thu nhỏ khi nội dung ít */
                max-width: 80%; /* Giới hạn chiều rộng */
                text-align: left; /* Căn lề trái */
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); /* Thêm hiệu ứng bóng đổ */
            }
            /* Áp dụng CSS cho tất cả các phần tử con bên trong để chuyển chữ sang phải và giữ màu */
            [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) * {
                color: inherit !important; /* Kế thừa màu chữ */
                width: inherit !important;
            }
            
            /* Ẩn đi avatar của user */  
            [data-testid="stChatMessageAvatarAssistant"] {
                position: absolute !important; 
                width: 0 !important;
                height: 0 !important;
                overflow: hidden !important;
                opacity: 0 !important;
                pointer-events: none !important;
            }
            
            /* Điều chỉnh spinner */
            [data-testid="stSpinner"] i {
                width: 30px;
                height: 30px;
                border-radius: 50% !important;
                display: inline-block;
                border-top: 2px solid #007bff; /* Màu xanh dương */
                border-right: 2px solid transparent;
                border-left: none;       
                border-bottom: none;
                box-sizing: border-box;
                animation: rotation 1s linear infinite; /* Nhanh hơn và có hiệu ứng ease-in-out */
            }  
            /* Hiệu ứng xoay không ổn định */
            @keyframes rotation {
                0% { transform: rotate(0deg); }  
                25% { transform: rotate(60deg); } /* Quay chậm từ 300° đến 60° */
                75% { transform: rotate(300deg); } /* Bắt đầu chậm lại */
                100% { transform: rotate(360deg); } /* Quay chậm từ 300° đến 60° */
            }
            
            /* Ô nhập Text_input */
            [data-baseweb="textarea"] {
                background-color: #FBF8FB; /* Màu nền */
                color: #333; /* Màu chữ xám đậm */
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); /* Thêm hiệu ứng bóng đổ */
            }
            /* Khi nhấn vào hộp nhập liệu, đổi viền ngoài thành đen */
            [data-baseweb="textarea"]:focus-within {
                border-color: #999999 !important;
                background-color: #FBF8FB; /* Màu nền */
                color: #333; /* Màu chữ xám đậm */
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); /* Thêm hiệu ứng bóng đổ */
            } 
            
            /* Ẩn đi khung của set_cookie */
            [data-testid="stElementContainer"]:has([data-testid="stCustomComponentV1"]){
                display: none !important;
            }
            
            /* Lớp overlay che phủ toàn bộ trang */
            [data-baseweb="modal"] {
            background: transparent; /* Nền mờ */
            }
            /* Lớp overlay che phủ toàn bộ trang */
            [data-baseweb="modal"] > div {
            background: transparent; /* Nền mờ */
            backdrop-filter: blur(5px); /* Làm mờ nền */
            }

            /* Nền của dialog */
            [aria-label="dialog"] {
                background: linear-gradient(to top, #E1F5FE, #FFFFFF);
            }

            /* Nút đóng dialog */
            [aria-label="Close"] {
            display: none;
            }
            [aria-label="dialog"] > div:first-child {
                display: none !important;
            }

            /* Xóa khung của Form */
            [data-testid="stForm"] {
                border: none;
            }

            /* Ô nhập Text_input */
            [data-baseweb="input"],
            [data-baseweb="input"] * {
                background-color: #FFFFFF; /* Màu nền */
                color: #333; /* Màu chữ xám đậm */
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); /* Thêm hiệu ứng bóng đổ */
            }
            /* Khi nhấn vào hộp nhập liệu, đổi viền ngoài thành đen */
            [data-baseweb="input"]:focus-within,
            [data-baseweb="input"] *:focus-within{
                border-color: #999999 !important;
                background-color: #FBF8FB; /* Màu nền */
                color: #333; /* Màu chữ xám đậm */
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); /* Thêm hiệu ứng bóng đổ */
            }     

            /* Căn chỉnh radio */
            [role="dialog"] [role="radiogroup"] {
                display: flex;
                justify-content: center;
            }

            /* Cảnh báo */
            [aria-label="dialog"][data-baseweb="notification"]{
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); /* Thêm hiệu ứng bóng đổ */
                background-color: rgb(249 240 172); /* Màu nền */
            }
                
            /* Nút gửi ở trong form */
            [data-testid="stFormSubmitButton"]{
                display: flex;
                justify-content: center;
            }
            [data-testid="stBaseButton-secondaryFormSubmit"]{
                padding: 0.4em 1em;
            }   
            
            [data-testid="stDialog"] > div {
                padding: 0 !important;
            }
            
            /* Nút gửi ở ngoài form */
            [data-testid="stButton"]{
                display: flex;
                justify-content: center;
            }
            [data-testid="stBaseButton-secondary"]{
                padding: 0.4em 1em;
            }   
            
            [data-testid="stButtonGroup"] {
                display: flex;
                justify-content: left; /* căn ngang giữa */
                align-items: center;     /* căn dọc giữa */
            }
            
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) {
                display: flex;
                justify-content: left; /* căn ngang giữa */
                align-items: center;     /* căn dọc giữa */
                max-width: 140px;
            }
            
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) * {
                max-width: 140px;
            }
            
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {
                display: flex;
                justify-content: left; /* căn ngang giữa */
                align-items: center;     /* căn dọc giữa */
                min-width: 140px;
                max-width: 140px;
            }            
            
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) * {
                min-width: 140px;
                max-width: 140px;
            }
                        
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) [data-testid="stButton"] {
                display: flex;
                justify-content: left; /* căn ngang giữa */
                align-items: center;     /* căn dọc giữa */
                flex: 1;
            }
            

        </style>    
        """,
        unsafe_allow_html=True,
    )
    