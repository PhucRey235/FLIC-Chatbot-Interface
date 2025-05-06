
# Công cụ RAG – Tìm Kiếm Thông Tin Trung Tâm (MongoDB)

**Chức năng chính:**

- Truy xuất thông tin về:
  - Chính sách
  - Khóa học
  - Lịch thi
  - Lệ phí
  - Thủ tục đăng ký
  - Nội dung đào tạo
  - Ưu đãi
- Hỗ trợ chatbot trả lời nhanh, chính xác các câu hỏi khách hàng.

---

## Quy tắc xử lý truy vấn người dùng

1. **Chỉnh sửa lỗi chính tả** tự động trước khi tìm kiếm.
2. **Chuẩn hóa từ khóa**:
   - `CNTT` / `Tin học` → `công nghệ thông tin`
   - `Học phí` → `lệ phí`
   - `Liên kết` / `link` → `liên kết`
3. **Loại bỏ** các từ không cần thiết (`cơ bản`, `nâng cao`) khi tìm chủ đề “công nghệ thông tin”.
4. **Phân đoạn truy vấn** nếu quá dài, giữ từng cụm từ khóa chính.
5. Trả về kết quả dạng **bullet** ngắn gọn, dễ đọc.
