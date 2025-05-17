import base64  # Dùng để mã hóa chuỗi theo Base64 cho phần Authorization
import json    # Dùng để xử lý dữ liệu JSON
import requests  # Thư viện gửi HTTP request (GET, POST)


class SpeedSMSAPI:
    # URL gốc của API SpeedSMS
    API_URL = "https://api.speedsms.vn/index.php"

    def __init__(self, access_token):
        """
        Hàm khởi tạo class, lưu access token của người dùng.
        access_token: chuỗi mã xác thực để gọi API SpeedSMS
        """
        self.access_token = access_token

    def _get_auth_header(self):
        """
        Tạo header Authorization theo chuẩn Basic Auth.
        SpeedSMS dùng access token như tên người dùng và bỏ trống mật khẩu.
        """
        user_credentials = f"{self.access_token}:x"  # ":x" là mặc định yêu cầu bởi SpeedSMS
        # Mã hóa chuỗi user_credentials thành Base64
        basic_auth = base64.b64encode(user_credentials.encode("utf-8")).decode("utf-8")
        # Trả về dictionary chứa Authorization header
        return {
            "Authorization": f"Basic {basic_auth}"
        }

    def get_user_info(self):
        """
        Gửi yêu cầu GET đến API để lấy thông tin tài khoản người dùng.
        Trả về: JSON dạng chuỗi
        """
        url = f"{self.API_URL}/user/info"  # Tạo URL
        headers = self._get_auth_header()  # Tạo header xác thực
        response = requests.get(url, headers=headers)  # Gửi request GET
        response.raise_for_status()  # Nếu lỗi HTTP thì raise exception
        return response.text  # Trả lại nội dung phản hồi dạng chuỗi

    def send_sms(self, to, content, sms_type, sender=''):
        """
        Gửi SMS đến 1 số điện thoại.

        to: số điện thoại người nhận (chuỗi, ví dụ: "0989123456")
        content: nội dung tin nhắn
        sms_type: loại tin nhắn (1 = brandname, 2 = SMS thường, 3 = quảng cáo)
        sender: tên brandname nếu dùng SMS brandname
        Trả về: chuỗi JSON phản hồi từ SpeedSMS
        """
        url = f"{self.API_URL}/sms/send"  # URL API gửi SMS
        headers = self._get_auth_header()  # Header xác thực
        headers["Content-Type"] = "application/json"  # Loại nội dung là JSON

        # Tạo payload dữ liệu gửi đi
        payload = {
            "to": [to],  # Danh sách số điện thoại nhận
            "content": self._encode_non_ascii(content),  # Encode ký tự unicode
            "type": sms_type,  # Loại tin nhắn
            "sender": sender  # Brandname nếu có
        }

        # Gửi yêu cầu POST đến SpeedSMS API
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Nếu lỗi HTTP thì raise exception
        return response  # Trả lại phản hồi từ server

    def _encode_non_ascii(self, value):
        """
        Encode các ký tự không phải ASCII sang mã Unicode (dạng \\uXXXX)
        Giúp tránh lỗi khi gửi ký tự tiếng Việt hoặc ký tự đặc biệt.
        """
        return ''.join(f'\\u{ord(c):04x}' if ord(c) > 127 else c for c in value)
