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

# Đường dẫn tới file credential
CREDENTIALS_PATH = "credentials.json"

# Cấu hình credentials
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

# Khởi tạo client BigQuery
client = bigquery.Client(credentials=credentials, project=credentials_dict['project_id'])

import pandas as pd
import random
from datetime import datetime, timedelta
from unidecode import unidecode

random.seed(42)
current_date = datetime.now().date()

# HocVien
last_names = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Vũ', 'Đặng', 'Bùi', 'Đỗ', 'Phan']
middle_names = ['Văn', 'Thị', 'Minh', 'Hữu', 'Thành', 'Quốc', 'Ngọc', 'Tuấn', 'Út', 'Anh']
first_names = ['An', 'Bình', 'Chi', 'Dung', 'Hương', 'Kiệt', 'Lan', 'My', 'Phúc', 'Quỳnh',
               'Quang', 'Sơn', 'Thảo', 'Trang', 'Hạnh', 'Loan', 'Mai', 'Nam', 'Oanh', 'Phương',
               'Tâm', 'Uyên', 'Vy', 'Xuân', 'Yến', 'Khánh', 'Hải', 'Giang', 'Đức', 'Hồ']

# Giả sử có 30 sinh viên, ta muốn khoảng 60% đủ điều kiện thi
num_students = 30
pct_eligible = 0.6
eligible_indices = set(random.sample(range(num_students), int(num_students * pct_eligible)))

students = []
for i in range(num_students):
    # Nếu i trong nhóm đủ điều kiện, enroll cách current_date 14–40 ngày
    if i in eligible_indices:
        enroll = current_date - timedelta(days=random.randint(14, 40))
    else:
        # Nhóm còn lại: enroll trong khoảng 0–13 ngày (chưa đủ 2 tuần)
        enroll = current_date - timedelta(days=random.randint(0, 13))
    dob = datetime(
        random.randint(2003, 2006),
        random.randint(1, 12),
        random.randint(1, 28)
    ).date()
    gender = random.choice(['Nam','Nữ'])
    fn = first_names[i]
    phone = f"09{random.randint(10000000,99999999)}"
    ma_sv = f"2111240{str(random.randint(0, 30)).zfill(2)}{random.randint(1, 3)}{str(random.randint(0, 40)).zfill(2)}"

    students.append({
        'idHocVien': i+1,
        'MaSV': ma_sv,
        'Ho': f"{random.choice(last_names)} {random.choice(middle_names)}",
        'Ten': fn,
        'NgaySinh': dob.strftime('%Y-%m-%d'),
        'GioiTinh': gender,
        'DienThoai': phone,
        'Email': f"{ma_sv}@due.udn.vn",
        'NgayHoc': enroll.strftime('%Y-%m-%d')
    })

# Tiếp tục như bình thường: dựng df_HocVien từ students
df_HocVien = pd.DataFrame(students).astype({
    'idHocVien':'int32','MaSV':'string','Ho':'string','Ten':'string',
    'NgaySinh':'string','GioiTinh':'string','DienThoai':'string','Email':'string','NgayHoc':'string'
})

# HocVien_Lop
hocvien_lop = []
for i, sv in enumerate(students):
    id_lop = 1 if i < len(students)//2 else 2  # nửa đầu là CB, nửa sau là NC
    hocvien_lop.append({
        'idHocVien_lop': sv['idHocVien'],
        'idHocVien': sv['idHocVien'],
        'idLop': id_lop,
        'SoTienKhuyenMai': random.choice([0,500000,1000000]),
        'NgayXepLop': (datetime.strptime(sv['NgayHoc'],'%Y-%m-%d')+timedelta(days=1)).date().strftime('%Y-%m-%d')
    })
    
df_HocVien_Lop = pd.DataFrame(hocvien_lop).astype({
    'idHocVien_lop':'int32','idHocVien':'int32','idLop':'int32',
    'SoTienKhuyenMai':'int64','NgayXepLop':'string'
})

# Lịch thi & Phòng thi
lich, phong = [], []
lid = pid = 1
for svl in hocvien_lop:
    nh = datetime.strptime(df_HocVien.loc[df_HocVien['idHocVien']==svl['idHocVien'],'NgayHoc'].iat[0], '%Y-%m-%d').date()
    if current_date >= nh + timedelta(weeks=2):
        ngkt = (nh + timedelta(weeks=2)).strftime('%Y-%m-%d')
        lich.append({'idLichThi':lid,'idKhoaThi':1 if svl['idLop']==1 else 2,
                     'BuoiThi':'Sáng','NgayThi':ngkt,'GioThi':'08:00-10:00'})
        phong.append({'idPhongThi':pid,'idKhoaThi':1 if svl['idLop']==1 else 2,
                      'PhongThi':f'Phòng {100+pid}','idLichThi':lid,'idCapDo':svl['idLop']})
        lid+=1; pid+=1

df_LichThi = pd.DataFrame(lich).astype({
    'idLichThi':'int32','idKhoaThi':'int32','BuoiThi':'string',
    'NgayThi':'string','GioThi':'string'
})
df_PhongThi = pd.DataFrame(phong).astype({
    'idPhongThi':'int32','idKhoaThi':'int32','PhongThi':'string',
    'idLichThi':'int32','idCapDo':'int32'
})

# KhóaThi_ThiSinh & Điểm
kts, dt_nc, dt_cb = [], [], []
idx = 1
for svl in hocvien_lop:
    nh = datetime.strptime(df_HocVien.loc[df_HocVien['idHocVien']==svl['idHocVien'],'NgayHoc'].iat[0], '%Y-%m-%d').date()
    if current_date >= nh + timedelta(weeks=2):
        # Tìm lịch thi gần nhất khớp idKhoaThi và idCapDo (vì mỗi học viên có thể có ngày học khác nhau)
        matching_lich = df_LichThi[df_LichThi['idKhoaThi'] == svl['idLop']]
        matching_phong = df_PhongThi[(df_PhongThi['idKhoaThi'] == svl['idLop']) & (df_PhongThi['idCapDo'] == svl['idLop'])]

        if not matching_lich.empty and not matching_phong.empty:
            rec_lich = matching_lich.iloc[0]
            rec_phong = matching_phong.iloc[0]

            exam_date = datetime.strptime(rec_lich['NgayThi'],'%Y-%m-%d').date() + timedelta(weeks=2)
            done = current_date >= exam_date

            entry = {
                'idKhoaThi_ThiSinh': idx,
                'idKhoaThi': rec_lich['idKhoaThi'],
                'idHocVien_Lop': svl['idHocVien_lop'],
                'idCapDo': svl['idLop'],
                'idPhongThi': rec_phong['idPhongThi'],  # 🔁 dùng id phòng thi
                'VangThi': False,
                'Xeploai': None,
                'SoHieuChungChi': f'CNTT-{idx:03d}'
            }

            if done:
                if svl['idLop']==1:
                    lt, th = round(random.uniform(0,10), 1), round(random.uniform(0,10), 1)
                    passed = lt>=5 and th>=5
                    entry['Xeploai'] = 'Đạt' if passed else 'Không đạt'
                    dt_nc.append({'idDiemThi':idx,'idKhoaThi_ThiSinh':idx,
                                'LT_Word':lt,'TH_Word':th,
                                'LT_Excel':random.uniform(0,10),'TH_Excel':random.uniform(0,10),
                                'LT_PP':random.uniform(0,10),'TH_PP':random.uniform(0,10)})
                else:
                    lt, th = round(random.uniform(0,10), 1), round(random.uniform(0,10), 1)
                    passed = lt>=5 and th>=5
                    entry['Xeploai'] = 'Đạt' if passed else 'Không đạt'
                    dt_cb.append({'idDiemThi':idx,'idKhoaThi_ThiSinh':idx,
                                'LyThuyet':lt,'ThucHanh':th})
            kts.append(entry)
            idx+=1

df_KhoaThi_ThiSinh = pd.DataFrame(kts).astype({
    'idKhoaThi_ThiSinh':'int32','idKhoaThi':'int32','idHocVien_Lop':'int32',
    'idCapDo':'int32','idPhongThi':'int32','VangThi':'bool',
    'Xeploai':'string','SoHieuChungChi':'string'
})
df_DiemThiNC = pd.DataFrame(dt_nc, columns=['idDiemThi','idKhoaThi_ThiSinh','LT_Word','TH_Word',
                                            'LT_Excel','TH_Excel','LT_PP','TH_PP']).astype({
    'idDiemThi':'int32','idKhoaThi_ThiSinh':'int32','LT_Word':'float64','TH_Word':'float64',
    'LT_Excel':'float64','TH_Excel':'float64','LT_PP':'float64','TH_PP':'float64'
})
df_DiemThiCB = pd.DataFrame(dt_cb, columns=['idDiemThi','idKhoaThi_ThiSinh','LyThuyet','ThucHanh']).astype({
    'idDiemThi':'int32','idKhoaThi_ThiSinh':'int32','LyThuyet':'float64','ThucHanh':'float64'
})


# Cấu hình thông tin dataset và bảng
dataset_id = "FLIC_ThongTinSinhVien"  # Thay bằng tên dataset bạn đã tạo trên BigQuery

# # Xóa toàn bộ bảng trong dataset
# tables = client.list_tables(dataset_id)
# for table in tables:
#     table_id = f"{dataset_id}.{table.table_id}"
#     client.delete_table(table_id, not_found_ok=True)
#     print(f"🗑️ Đã xóa bảng: {table_id}")

# Danh sách ánh xạ tên bảng và DataFrame tương ứng
table_map = {
    "HocVien": df_HocVien,
    "HocVien_Lop": df_HocVien_Lop,
    "SatHachCNTT_LichThi": df_LichThi,
    "SatHachCNTT_PhongThi": df_PhongThi,
    "SatHachCNTT_KhoaThi_ThiSinh": df_KhoaThi_ThiSinh,
    "SatHachCNTT_DiemThiNC": df_DiemThiNC,
    "SatHachCNTT_DiemThiCB": df_DiemThiCB
    # Nếu bạn có các bảng: SatHachCNTT_KhoaThi_Lop, SatHachCNTT_DMKhoaThi, SatHachCNTT_ThiSinh_MonThi
    # thì thêm DataFrame tương ứng vào đây
}

# Gửi từng bảng lên BigQuery
for table_name, df in table_map.items():
    table_id = f"{credentials_dict['project_id']}.{dataset_id}.{table_name}"
    job = client.load_table_from_dataframe(
        df,
        table_id,
        job_config=bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE"
        )
    )
    job.result()
    print(f"✅ Đã tải lên bảng {table_name} ({len(df)} dòng)")

print("🎉 Tất cả dữ liệu đã được đẩy lên BigQuery thành công.")
