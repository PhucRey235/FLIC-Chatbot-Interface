# model/mock_database.py
# File này chứa dữ liệu mock cho BigQuery, mô phỏng thông tin học viên và kết quả thi
# Sử dụng Python để tạo dữ liệu mẫu, có thể tích hợp với BigQuery sau

import pandas as pd  # Thư viện để tạo DataFrame cho dữ liệu mock
from google.cloud import bigquery
from google.oauth2 import service_account
import os
from dotenv import load_dotenv  # Nạp biến môi trường

# Nạp biến môi trường
load_dotenv()

# Bigquery credentials
TYPE_BQ = os.getenv("TYPE_BQ")   
PROJECT_ID_BQ = os.getenv("PROJECT_ID_BQ")  
PRIVATE_KEY_ID_BQ = os.getenv("PRIVATE_KEY_ID_BQ")  
PRIVATE_KEY_BQ = os.getenv("PRIVATE_KEY_BQ").replace("\\n", "\n")
CLIENT_EMAIL_BQ = os.getenv("CLIENT_EMAIL_BQ")  
CLIENT_ID_BQ = os.getenv("CLIENT_ID_BQ")  
AUTH_URI_BQ = os.getenv("AUTH_URI_BQ")  
TOKEN_URI_BQ = os.getenv("TOKEN_URI_BQ")  
AUTH_PROVIDER_X509_CERT_URL_BQ = os.getenv("AUTH_PROVIDER_X509_CERT_URL_BQ")  
CLIENT_X509_CERT_URL_BQ = os.getenv("CLIENT_X509_CERT_URL_BQ")  
UNIVERSE_DOMAIN_BQ = os.getenv("UNIVERSE_DOMAIN_BQ")   

# Tạo thông tin credentials từ biến môi trường
credentials_dict = {
    "type": TYPE_BQ,
    "project_id": PROJECT_ID_BQ,
    "private_key_id": PRIVATE_KEY_ID_BQ,
    "private_key": PRIVATE_KEY_BQ,
    "client_email": CLIENT_EMAIL_BQ,
    "client_id": CLIENT_ID_BQ,
    "auth_uri": AUTH_URI_BQ,
    "token_uri": TOKEN_URI_BQ,
    "auth_provider_x509_cert_url": AUTH_PROVIDER_X509_CERT_URL_BQ,
    "client_x509_cert_url": CLIENT_X509_CERT_URL_BQ,
    "universe_domain": UNIVERSE_DOMAIN_BQ,
}

# Bảng mock cho học viên (students)
# Dữ liệu mở rộng cho bảng học viên
students_data = pd.DataFrame({
    'student_id': [1, 2, 3, 4, 5],
    'name': ['Nguyễn Văn A', 'Trần Thị B', 'Lê Văn C', 'Phạm Minh D', 'Hoàng Thị E'],
    'email': ['vana@example.com', 'thib@example.com', 'venc@example.com', 'minhd@example.com', 'thie@example.com'],
    'enrollment_date': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-01', '2023-05-12'],
    'phone': ['0909123456', '0911223344', '0922334455', '0933445566', '0944556677'],
    'birth_date': ['1999-08-01', '2000-04-15', '1998-11-20', '2001-07-10', '2002-12-30'],
    'gender': ['Nam', 'Nữ', 'Nam', 'Nam', 'Nữ'],
    'course': ['TOEIC A', 'IELTS B', 'TOEIC A', 'Cambridge C1', 'IELTS B'],
    'level': ['Beginner', 'Intermediate', 'Beginner', 'Advanced', 'Intermediate'],
    'status': ['Đang học', 'Đã tốt nghiệp', 'Đang học', 'Đã tốt nghiệp', 'Đang học']
})

# Dữ liệu mở rộng cho bảng kết quả thi
test_results_data = pd.DataFrame({
    'result_id': [101, 102, 103, 104, 105, 106, 107],
    'student_id': [1, 2, 3, 1, 4, 5, 2],
    'test_type': ['TOEIC', 'IELTS', 'TOEIC', 'IELTS', 'Cambridge', 'IELTS', 'TOEIC'],
    'score': [850, 6.5, 920, 7.0, 180, 7.5, 700],
    'test_date': ['2024-05-01', '2024-06-15', '2024-07-20', '2024-08-10', '2024-09-05', '2024-10-12', '2024-12-01']
})

# Đường dẫn tới file credential
CREDENTIALS_PATH = "credentials.json"

# Cấu hình credentials
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

# Khởi tạo client BigQuery
client = bigquery.Client(credentials=credentials, project=credentials_dict['project_id'])

# Cấu hình thông tin dataset và bảng
dataset_id = "FLIC_ThongTinSinhVien"  # Thay bằng tên dataset bạn đã tạo trên BigQuery
students_table_id = f"{credentials_dict['project_id']}.{dataset_id}.students"
results_table_id = f"{credentials_dict['project_id']}.{dataset_id}.test_results"

# Gửi dữ liệu students lên BigQuery
job_students = client.load_table_from_dataframe(
    students_data,
    students_table_id,
    job_config=bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",  # Ghi đè dữ liệu cũ
    )
)
job_students.result()  # Đợi job hoàn thành

# Gửi dữ liệu test_results lên BigQuery
job_results = client.load_table_from_dataframe(
    test_results_data,
    results_table_id,
    job_config=bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
    )
)

job_results.result()

print("✅ Dữ liệu đã được tải lên BigQuery thành công.")
