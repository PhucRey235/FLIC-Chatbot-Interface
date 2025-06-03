
# Công cụ RAG Nâng Cao – Mở Rộng & Tinh Chỉnh Truy Vấn

**Mục tiêu:**

- Tăng khả năng tìm đúng thông tin ngay cả khi câu hỏi phức tạp hoặc nhập thiếu/nhầm từ.
- Áp dụng kỹ thuật: **query expansion**, **query reformulation**, **semantic search**, **pseudo‑relevance feedback**.

---

## 1. Tiền Xử Lý Truy Vấn

- **Sửa lỗi chính tả** và **chuẩn hóa từ đồng nghĩa** như trên.
- **Nhận diện thực thể** (TOEIC, CNTT, lịch thi…) để hiểu rõ ngữ cảnh.

---

## 2. Mở Rộng Truy Vấn (Query Expansion)

- Tự động thêm các từ khóa liên quan:
  - Ví dụ “lệ phí” → thêm “học phí”, “chi phí”.
  - “TOEIC” → thêm “thi TOEIC IIG”, “điểm TOEIC”.

---

## 3. Tinh Chỉnh Truy Vấn (Query Reformulation)

- Nếu không tìm ra kết quả, tái cấu trúc câu hỏi:
  - Thay đổi thứ tự từ khóa, loại bỏ mệnh đề phụ.
  - Ví dụ: “lệ phí TOEIC nhóm” → “TOEIC lệ phí nhóm”.

---

## 4. Semantic Search & Relevance Feedback

- Sử dụng **embedding** để so khớp ngữ nghĩa nếu không tìm thấy kết quả chính xác.
- Áp dụng **top‑k pseudo‑relevance**: dùng kết quả đầu tiên để mở rộng truy vấn lần 2.

---

## 5. Đầu Ra

- Trả lời dưới dạng **bullet list** rõ ràng.
- Nếu vẫn không có kết quả:
  > “Xin vui lòng liên hệ trực tiếp với Trung tâm Tiếng Anh FLIC để được hỗ trợ thêm.”
  >
