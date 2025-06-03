# Công cụ mô tả toàn bộ cấu trúc và dữ liệu mẫu của các bảng trong một dataset

## Khi được gọi, công cụ sẽ:
- Lấy danh sách tất cả các bảng trong dataset.
- Với mỗi bảng, sinh câu lệnh `CREATE TABLE` tương ứng (bao gồm tên bảng và kiểu dữ liệu của các cột).
- Trích xuất một số dòng dữ liệu mẫu (mặc định là 2 dòng) để minh họa cho mỗi bảng.
- Đính kèm thêm phần mô tả các ràng buộc khóa chính và khóa ngoại (PK/FK) giữa các bảng.

## Đầu ra là một chuỗi văn bản để để tạo truy vấn và kiểm tra lại truy vấn đó, bao gồm:
1. Câu lệnh tạo bảng (CREATE TABLE) cho từng bảng.
2. Dữ liệu mẫu (sample rows) dưới dạng comment block.
3. Thông tin ràng buộc (constraint) dưới dạng bảng markdown.