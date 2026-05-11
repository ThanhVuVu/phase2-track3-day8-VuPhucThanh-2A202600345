# Báo cáo kết quả Lab Day 08

## 1. Thông tin sinh viên / nhóm

- Họ và tên: Vũ Phúc Thành
- Repo/commit: d:\phase2-track3-day8-langgraph-agent (Nộp bài cục bộ)
- Ngày thực hiện: 11/05/2026

## 2. Kiến trúc hệ thống (Architecture)

Hệ thống được xây dựng dưới dạng một đồ thị trạng thái (stateful graph) sử dụng thư viện LangGraph. Quy trình xử lý đi qua các bước (node) được kiểm soát chặt chẽ:
- **Các Nodes chính**:
    - `intake`: Tiếp nhận yêu cầu, khởi tạo trạng thái và ghi nhật ký.
    - `classify`: Phân tích yêu cầu bằng logic từ khóa có ưu tiên để điều hướng đến đúng bộ phận xử lý.
    - `answer`: Xử lý các câu hỏi thông tin đơn giản.
    - `tool`: Thực thi các công cụ giả lập (ví dụ: tra cứu cơ sở dữ liệu).
    - `evaluate`: Đánh giá kết quả của công cụ và quyết định xem có cần thử lại (retry) hay không.
    - `clarify`: Yêu cầu khách hàng cung cấp thêm thông tin còn thiếu.
    - `risky_action`: Xử lý các thao tác nhạy cảm (xóa dữ liệu, đổi mật khẩu).
    - `approval`: Node dừng để chờ con người phê duyệt (Human-in-the-loop).
    - `retry`: Quản lý bộ đếm số lần thử lại và logic quay vòng.
    - `dead_letter`: Trạm dừng cuối cho các yêu cầu thất bại sau nhiều lần thử lại.
    - `finalize`: Tổng hợp câu trả lời cuối cùng và ghi nhận luồng xử lý thực tế.
- **Các Edges**: Kết nối các node theo trình tự logic. Sử dụng **Conditional Edges** (Cạnh điều kiện) để phân nhánh từ các node `classify`, `evaluate`, `approval`, và `retry`.

## 3. Cấu trúc trạng thái (State Schema)

`AgentState` được thiết kế kết hợp giữa các trường "Ghi đè" (để lưu trạng thái hiện tại) và các trường "Cộng dồn" (để lưu vết lịch sử phục vụ kiểm toán).

| Trường dữ liệu | Reducer | Mục đích |
|---|---|---|
| messages | append | Lưu giữ toàn bộ lịch sử hội thoại để làm ngữ cảnh. |
| steps | append | Truy vết mọi node đã đi qua để tính toán chính xác các chỉ số hiệu suất. |
| events | append | Lưu trữ chi tiết các đối tượng LabEvent phục vụ gỡ lỗi (debugging). |
| errors | append | Thu thập tất cả các lỗi tạm thời để phân tích trong báo cáo cuối cùng. |
| route | overwrite | Lưu giữ phân loại điều hướng hiện tại. |
| attempt | overwrite | Theo dõi số lần thử lại để giới hạn vòng lặp. |

## 4. Kết quả các kịch bản (Scenario Results)

Hệ thống đã đạt **tỷ lệ thành công 100%** trên tất cả các kịch bản kiểm thử (Số liệu sau khi reset dữ liệu sạch).

| Kịch bản | Luồng dự kiến | Luồng thực tế | Thành công | Thử lại | Ngắt (HITL) |
|---|---|---|---:|---:|---:|
| S01_simple | simple | simple | Có | 0 | 0 |
| S02_tool | tool | tool | Có | 0 | 0 |
| S03_missing | missing_info | missing_info | Có | 0 | 0 |
| S04_risky | risky | risky | Có | 0 | 1 |
| S05_error | error | error | Có | 2 | 0 |
| S06_delete | risky | risky | Có | 0 | 1 |
| S07_dead_letter | error | error | Có | 1 | 0 |

## 5. Phân tích lỗi (Failure Analysis)

Chúng tôi đã thiết kế và triển khai xử lý cho hai kịch bản lỗi chính:

1. **Lỗi thử lại hoặc lỗi công cụ**: Trong kịch bản **S05**, công cụ giả lập tạo ra các lỗi tạm thời. Hệ thống đã điều hướng đúng sang `evaluate`, sau đó đến `retry` để tăng bộ đếm `attempt`. Khi lỗi được khắc phục, hệ thống đi đến `answer` thành công. Ở **S07**, hệ thống ghi nhận lỗi và thực hiện các bước phục hồi theo đúng quy trình retry.
2. **Hành động nguy hiểm không được phê duyệt**: Trong kịch bản **S06**, một yêu cầu xóa dữ liệu được phân loại là `risky`. Đồ thị đã dừng lại tại node `approval`. Khi giả lập "Từ chối phê duyệt" (`approved: False`), hệ thống đã chuyển hướng sang `clarify` thay vì thực thi công cụ nguy hiểm, chứng minh khả năng kiểm soát an toàn hiệu quả.

## 6. Minh chứng về Lưu trữ và Khôi phục (Persistence)

Hệ thống sử dụng bộ lưu trữ **SQLite Checkpointer** chuyên nghiệp (`SqliteSaver`) với chế độ **WAL (Write-Ahead Logging)**:
- **Minh chứng**: Mỗi phiên chạy được gán một `thread_id` duy nhất (ví dụ: `thread-S01_simple`).
- **Khôi phục**: Trạng thái được lưu vĩnh viễn trong file `checkpoints.db`. Các con số nhỏ và sạch trong bảng trên cho thấy hệ thống có khả năng quản lý trạng thái cô lập và bền vững giữa các lần chạy.

## 7. Các phần mở rộng (Extension Work)

1. **Trực quan hóa đồ thị**: Sử dụng script `scripts/export_graph.py` để xuất sơ đồ Mermaid, cung cấp cái nhìn trực quan về kiến trúc hệ thống.
2. **SQLite Persistence**: Nâng cấp từ bộ nhớ tạm (`MemorySaver`) lên `SqliteSaver` để đáp ứng tiêu chuẩn của band điểm 90-100.
3. **Cải tiến Metrics**: Cập nhật bộ máy đo lường để sử dụng danh sách `steps` chuyên dụng thay vì phân tích các sự kiện thô, đảm bảo độ chính xác 100%.
4. **Vệ sinh mã nguồn**: Dọn dẹp hoàn toàn hơn 40 lỗi lint/type để vượt qua các trình kiểm tra `ruff` và `mypy` 100%.

## 8. Kế hoạch cải tiến (Improvement Plan)

Nếu có thêm thời gian, tôi sẽ ưu tiên các cải tiến sau để đưa hệ thống vào sản xuất:
1. **Phân loại bằng LLM**: Thay thế logic từ khóa bằng một mô hình ngôn ngữ lớn (như Llama-3-8B) để hiểu ý định người dùng một cách tự nhiên và chính xác hơn.
2. **Tìm kiếm Vector (RAG)**: Tích hợp hệ thống tìm kiếm ngữ nghĩa vào `tool` node để trả về kết quả thực tế từ cơ sở tri thức thay vì kết quả giả lập.
3. **Giao diện người dùng tương tác**: Xây dựng giao diện Streamlit để theo dõi lịch sử trạng thái trực quan và cho phép con người phê duyệt các yêu cầu `risky` ngay trên giao diện.
