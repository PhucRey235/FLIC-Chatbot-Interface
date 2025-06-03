# Công cụ RAG truy xuất thông tin khóa học công nghệ thông tin cơ bản và nâng cao, TOEIC

## Chức năng chính

- Truy xuất thông tin sau:
    * Thông tin về chứng chỉ.
    * Lệ phí đăng ký dự thi và học ôn.
    * Lịch thi.
    * Thủ tục và hồ sơ đăng kýdự thi và học ôn.
    * Thông tin liên hệ.

## Quy tắc tạo truy xuất RAG

1. **Chỉnh sửa lỗi chính tả** tự động trước khi tìm kiếm.
2. **Chuẩn hóa từ khóa** (chuyển về dạng thống nhất): `CNTT` / `Tin học` / `công nghệ thông tin` / → `công nghệ thông tin .`
3. Sử dụng nội dung lịch sử đoạn hội thoại giữa Chatbot và người dùng để tạo ra câu truy xuất RAG.
4. Chuẩn hóa tất cả truy vấn thành **chữ thường** và có dấu tiếng Việt.
5. Câu truy vấn: `Thông tin cần truy vấn` + `Khóa học cần truy vấn`