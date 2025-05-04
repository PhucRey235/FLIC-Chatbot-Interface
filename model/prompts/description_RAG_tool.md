
# Công cụ tìm kiếm thông tin trung tâm từ hệ thống RAG (MongoDB)

**Chức năng:**

- Lấy thông tin cơ bản về trung tâm như:
  - **Chính sách**
  - **Khóa học**
  - **Lịch thi**
  - **Lệ phí**
  - **Thủ tục đăng ký**
  - **Nội dung đào tạo**
  - **Ưu đãi**
- Hỗ trợ chatbot trả lời câu hỏi **chính xác** và **nhanh chóng**.

---

## Quy tắc xử lý truy vấn người dùng

1. **Sửa lỗi chính tả** nếu người dùng nhập sai.
2. Các từ sau được xem là **tương đương**:
   - `CNTT`, `Tin học`, `công nghệ thông tin` → **Chuyển tất cả thành:** `công nghệ thông tin`
     - **Không cần ghi**: `cơ bản` hay `nâng cao`
   - `Học phí`, `lệ phí` → **Chuyển tất cả thành:** `lệ phí`
   - `Liên kết`, `đường dẫn`, `link` → **Chuyển tất cả thành:** `liên kết`
