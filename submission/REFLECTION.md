# Reflection — Lab 19

**Tên:** Lâm Hoàng Hải
**Cohort:** _`<A20-K1>`_
**Path đã chạy:** _docker_

---

## Câu hỏi (≤ 200 chữ)

> Trên golden set 50 queries, mode nào thắng ở loại query nào (`exact` /
> `paraphrase` / `mixed`), và tại sao? Khi nào bạn **không** dùng hybrid
> (i.e. khi nào pure BM25 hoặc pure vector là lựa chọn đúng)?

Trong golden set 50 queries:

- **Exact (Chính xác):** BM25 và Hybrid cùng thắng (96.7%). BM25 vượt trội nhờ khả năng khớp từ khóa kỹ thuật verbatim (như "lazy loading", "service worker") mà không bị nhiễu bởi các khái niệm tương đồng.
- **Paraphrase (Diễn giải):** Kết quả khá thấp trên cả 3 mode (24-33%) do model `bge-small-en` hỗ trợ tiếng Việt hạn chế. Tuy nhiên, BM25 vẫn nhỉnh hơn một chút nhờ các từ khóa gốc còn sót lại.
- **Mixed (Hỗn hợp):** Hybrid thắng tuyệt đối (100.0%), vượt qua cả BM25 (97.0%) và Semantic (98.5%). Điều này chứng minh sức mạnh của Hybrid trong việc kết hợp cả tín hiệu từ khóa và ngữ nghĩa để xử lý các câu hỏi thực tế.

**Khi nào KHÔNG dùng hybrid:**

- Dùng **Pure BM25**: Khi tìm kiếm các mã định danh (IDs), số hiệu sản phẩm, hoặc trong hệ thống yêu cầu độ trễ cực thấp (latency-critical) mà không thể tốn thời gian cho bước embedding.
- Dùng **Pure Vector**: Khi tìm kiếm trên dữ liệu đa phương thức (hình ảnh, âm thanh) hoặc khi muốn hoàn toàn ưu tiên ý tưởng thay vì câu chữ (ví dụ: tìm các bài báo cùng quan điểm nhưng dùng bộ từ vựng hoàn toàn khác nhau)._

---

## Điều ngạc nhiên nhất khi làm lab này

Điều ngạc nhiên nhất là ở notebook 4 khi dùng SQLite, latency không thể < 10ms dù chạy lại nhiều lần, thậm chí có lúc spike > 20ms, kết quả hoàn toàn non deterministic.

---

## Bonus challenge

- [X] Đã làm bonus (xem `bonus/`)
- [ ] Pair work với: _<tên đồng đội nếu có>_
