# Architecture — Personal AI Memory System (POC)

## Overview
Hệ thống này kết hợp **Episodic Memory** (trí nhớ sự kiện - Vector Store) và **Stable User Profile** (hồ sơ người dùng - Feature Store) để tạo ra một ngữ cảnh cá nhân hóa sâu sắc cho trợ lý AI.

### Sơ đồ kiến trúc (Mermaid)
```mermaid
graph TD
    User((User)) -->|Input: "Recall X"| Agent[HybridMemoryAgent]
    Agent -->|1. Lookup Features| Feast[Feast Online Store]
    Feast -->|reading_speed, topic_affinity| Agent
    Agent -->|2. Vector Search + User Filter| Qdrant[Qdrant Vector DB]
    Qdrant -->|Top-K Memories| Agent
    Agent -->|3. Assemble Context| Prompt[Final Prompt Context]
    Prompt -->|Optional| LLM[LLM / Generator]
```

---

## 3 Quyết định kiến trúc với Tradeoff

### 1. Chiến lược Chunking: Paragraph-level
*   **Quyết định**: Chúng tôi chia nhỏ các ghi chú/hội thoại theo từng đoạn văn (paragraph) thay vì từng câu hoặc toàn bộ tài liệu.
*   **Tradeoff**: 
    *   *Retreival Quality*: Cao hơn so với việc lưu cả tài liệu vì tránh pha loãng vector (semantic dilution).
    *   *Storage Cost*: Tăng số lượng vectors cần lưu trữ so với lưu cả tài liệu, nhưng chấp nhận được với quy mô cá nhân.
    *   *Context Window*: Giúp đưa được nhiều mẩu tin rời rạc nhưng liên quan vào context window hẹp của LLM.

### 2. Feature Schema: Tabular vs Embedding Features
*   **Quyết định**: Hiện tại POC dùng **Tabular Features** (reading_speed, topic_affinity) để demo sự đơn giản.
*   **Lý do**: Với trợ lý cá nhân, các thuộc tính như "ngôn ngữ ưu tiên" là tường minh và không thay đổi quá nhanh. Tuy nhiên, trong tương lai, `topic_affinity` nên được chuyển thành **Embedding Feature** (lấy trung bình vector của 100 queries gần nhất) để phản ánh sự thay đổi sở thích một cách "mượt" hơn thay vì các category cứng.

### 3. Freshness Strategy: Push-Pull Hybrid
*   **Quyết định**:
    *   **Sub-second (Vectors)**: Ngay khi user nói gì đó, `remember()` sẽ đẩy vào Qdrant ngay lập tức.
    *   **5-min (Profile)**: Các chỉ số như `queries_last_hour` được cập nhật qua batch job định kỳ.
*   **Tradeoff**: Chúng tôi ưu tiên sự "nhạy bén" của trí nhớ sự kiện (user muốn trợ lý nhớ ngay những gì vừa nói) hơn là sự cập nhật tức thì của các chỉ số thống kê dài hạn.

---

## Loại bỏ lựa chọn sai: Episodic Memory trong Feature Store
Tôi đã xem xét việc lưu trữ toàn bộ episodic memory (vectorized) như một `FeatureView` trong Feast. Tuy nhiên, tôi đã loại bỏ ý tưởng này vì:
*   **Re-index Cycle**: Trí nhớ sự kiện cần được cập nhật liên tục (mỗi câu nói). Feast `materialization` thường được thiết kế cho batch hoặc streaming pipeline phức tạp hơn.
*   **Query Pattern**: Qdrant hỗ trợ lọc nâng cao (payload filtering) và các thuật toán HNSW tối ưu cho vector search, điều mà các online store của Feast (như Redis/SQLite) không chuyên dụng bằng.

---

## Vietnamese-Context Considerations
*   **Code-switching (Vinglish)**: Người dùng Việt thường trộn lẫn tiếng Anh (ví dụ: "cloud computing", "backend"). Chúng tôi sử dụng model `BAAI/bge-small-en-v1.5` dù là English-trained nhưng có khả năng xử lý tốt các keyword kỹ thuật này. Trong tương lai, `bge-m3` sẽ là lựa chọn tốt hơn cho multilingual.
*   **NLP Tokenizer**: Hiện tại dùng whitespace split đơn giản. Với tiếng Việt, điều này có thể làm giảm hiệu quả BM25 nhưng với Vector Search thì ít ảnh hưởng hơn vì model đã học được embedding cho các cụm từ phổ biến.

---

## Honest Limitations
*   **Privacy**: Hiện tại filter theo `user_id` chỉ ở mức logic payload. Trong production, cần isolation ở mức collection hoặc encrypted vectors.
*   **CRUD**: POC chưa hỗ trợ xóa hoặc cập nhật trí nhớ (ví dụ: user muốn trợ lý "quên" một sự kiện).
*   **Memory Decay**: Chưa có cơ chế quên đi những ký ức quá cũ hoặc ít được truy cập.

---
*Contributors: Antigravity AI*
