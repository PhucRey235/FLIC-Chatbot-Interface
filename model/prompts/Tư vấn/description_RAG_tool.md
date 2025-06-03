# Công cụ RAG – Tìm Kiếm Thông Tin Trung Tâm (MongoDB)

**Chức năng chính:**

* Truy xuất thông tin chi tiết về các hạng mục sau (truy xuất riêng lẻ theo yêu cầu của người dùng):

  * **Chính sách** của trung tâm.
  * **Lệ phí** đăng ký dự thi và học ôn.
  * **Lịch thi**.
  * **Thủ tục đăng ký** dự thi và học ôn (hướng dẫn chi tiết đầy đủ nội dung).
  * Các chương trình **ưu đãi**.
  * **Kiểm tra trình độ TOEIC để tư vấn đăng ký học ôn** (bao gồm hướng dẫn chi tiết làm bài và gửi kết quả).
  * **Đánh giá kết quả bài kiểm tra TOEIC** (bao gồm đánh giá kỹ năng và tư vấn lớp học).

## Quy tắc tạo truy xuất RAG

1. **Chỉnh sửa lỗi chính tả** tự động trước khi tìm kiếm.
2. **Chuẩn hóa từ khóa** (chuyển về dạng thống nhất): `CNTT` / `Tin học` / `công nghệ thông tin` / → `công nghệ thông tin .`
3. Sử dụng nội dung lịch sử đoạn hội thoại giữa Chatbot và người dùng để tạo ra câu truy xuất RAG.
4. Chuẩn hóa tất cả truy vấn thành **chữ thường** và có dấu tiếng Việt.
