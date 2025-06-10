import requests
import json
import uuid

def send_OTP(ma_OTP, phone):
    url = "https://rest.esms.vn/MainService.svc/json/SendMultipleMessage_V4_post_json/"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "ApiKey": "8593C92466FCD8A29BD20F04BFD7F9",
        "SecretKey": "8EA766D76BD00C6B3B863873DD0379",
        "Content": f"{ma_OTP} la ma xac minh dang ky Baotrixemay cua ban",
        "Phone": str(phone),
        "Brandname": "Baotrixemay",
        "SmsType": "2",
        "IsUnicode": "0",
        "RequestId": "test-request-id-21",
        "campaignid": "Test Campaign",
        "CallbackUrl": "https://esms.vn/webhook/"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    print("Status Code:", response.status_code)
    print("Response Body:", response.text)

    return response.status_code

def send_OTP_test(ma_OTP, phone):
    return 100
    