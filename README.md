# 🚀 CareerBridge AI — Hệ Thống AI Kết Nối Nghề Nghiệp & Tuyển Dụng Sinh Viên

> Nền tảng ứng dụng Trí Tuệ Nhân Tạo (AI) toàn diện hỗ trợ Trung tâm Hướng nghiệp kết nối sinh viên với các cơ hội thực tập và việc làm phù hợp, tối ưu hồ sơ năng lực (ATS CV), mô phỏng phỏng vấn thực tế và dự báo xu hướng thị trường lao động.

---

## 🎯 1. Bài toán và Giải pháp

### Bài toán
- **Thực trạng**: Trung tâm hướng nghiệp và các trường đại học gặp nhiều khó khăn khi kết nối sinh viên với doanh nghiệp:
  1. Thông tin tuyển dụng phân tán, không có chuẩn hóa dữ liệu.
  2. Việc ghép nối thủ công tốn nhiều nguồn lực và không phản ánh chính xác năng lực, điểm mạnh hay nguyện vọng cụ thể của từng sinh viên.
  3. Sinh viên chưa biết cách tối ưu hóa CV theo chuẩn ATS, thiếu kỹ năng phỏng vấn thực tế và không rõ lộ trình bổ sung kỹ năng còn thiếu.
  4. Doanh nghiệp mất nhiều thời gian sàng lọc hàng trăm CV không phù hợp.

### Giải pháp của CareerBridge AI
Hệ thống giải quyết triệt để 5 trụ cột cốt lõi:
1. **🤖 AI Matching Engine**: Thuật toán Hybrid ML (TF-IDF Vector Space, Cosine Similarity, Ma trận Kỹ năng đa trọng số và GPA) tự động phân tích hồ sơ năng lực và JD để tính điểm phù hợp (Match Score %), đưa ra phân tích chi tiết (Điểm mạnh, Lỗ hổng kỹ năng, Lời khuyên trước khi nộp đơn).
2. **📄 AI CV & ATS Analyzer**: Chấm điểm ATS (0-100), phát hiện từ khóa chuyên ngành còn thiếu, tự động viết lại các bullet points kinh nghiệm theo chuẩn quốc tế **STAR (Situation - Task - Action - Result)** có chỉ số định lượng.
3. **🎙️ AI Mock Interview Simulator**: Mô phỏng phỏng vấn thực chiến với 3 vòng (Kỹ thuật, Tình huống kiến trúc, Hành vi STAR). Hỗ trợ nhận diện giọng nói tiếng Việt bằng micro 🎙️, chấm điểm tức thì trên 4 tiêu chí và đưa ra câu trả lời mẫu 10/10.
4. **🗺️ AI Skill Gap & Career Roadmap**: Xác định khoảng cách kỹ năng giữa năng lực hiện tại và mục tiêu nghề nghiệp, sinh lộ trình học tập 4 giai đoạn cụ thể kèm tài nguyên uy tín.
5. **📈 Market Intelligence & Analytics**: Bảng điều khiển phân tích số liệu thời gian thực cho Trung tâm Hướng nghiệp: tỷ lệ sinh viên có việc làm sau tốt nghiệp, top kỹ năng đang thiếu hụt và thang lương thị trường.

---

## 🏗️ 2. Kiến trúc Hệ thống (System Architecture)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CAREERBRIDGE AI WEB APP                          │
│          Responsive Tailwind SPA • 3 Phân quyền: Student / Recruiter / Admin│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / REST API (JWT Auth)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FASTAPI BACKEND ENGINE                             │
│  ├── Auth & RBAC (Password Hash PBKDF2, JWT Tokens)                         │
│  ├── Job & Application Management Router                                    │
│  ├── Student Competency & Profile Router                                    │
│  └── Admin User Management & Analytics Router                               │
└──────────────────┬───────────────────────────────────┬──────────────────────┘
                   │                                   │
                   ▼                                   ▼
┌──────────────────────────────────────┐  ┌───────────────────────────────────┐
│           AI & ML ENGINES            │  │          PERSISTENCE LAYER        │
│  ├── Hybrid Vector TF-IDF Matching   │  │  ├── SQLite (WAL Mode, Relations) │
│  ├── Skill Taxonomy & Gap Analyzer   │  │  ├── User & Profile Models        │
│  ├── ATS Scorer & STAR Rewriter      │  │  ├── Job Postings & JDs           │
│  └── Real-time Mock Interview Engine │  │  └── Applications & Review Logs   │
└──────────────────────────────────────┘  └───────────────────────────────────┘
```

---

## 👥 3. Phân quyền Người dùng (Role-Based Access Control)

| Vai trò | Tài khoản Mẫu (Demo) | Mật khẩu | Tính năng chính |
| :--- | :--- | :--- | :--- |
| **🎓 Sinh viên** *(Student)* | `student@careerbridge.edu.vn` | `password123` | Khám phá việc làm & Điểm tương thích AI, Chấm điểm CV ATS, Phỏng vấn thử Mock Interview, Lộ trình kỹ năng, Quản lý đơn ứng tuyển |
| **🏢 Doanh nghiệp** *(Recruiter)* | `recruiter@careerbridge.edu.vn` | `password123` | Đăng tin tuyển dụng (JD), AI tự động tìm kiếm ứng viên toàn trường (Proactive Sourcing), Xem hồ sơ ứng viên xếp hạng theo AI Match Score, Duyệt và cập nhật trạng thái |
| **🏛️ Trung tâm Hướng nghiệp** *(Admin)* | `admin@careerbridge.edu.vn` | `password123` | Dashboard tỷ lệ việc làm, Thống kê thị trường & Top kỹ năng, Quản lý toàn bộ người dùng (Khóa/Mở khóa, Phân quyền), Giám sát tuyển dụng |

*(Hệ thống có thanh chuyển đổi vai trò nhanh 1-click ngay trên thanh Header để tiện kiểm thử!)*

---

## ⚡ 4. Hướng dẫn Khởi chạy & Triển khai

### Chạy Local:
```bash
# 1. Cài đặt thư viện
pip install -r requirements.txt

# 2. Khởi động máy chủ
python run_server.py
```
Mở trình duyệt truy cập: `http://localhost:8000`

### Triển khai Online (Có Public HTTPS URL):
Hệ thống tích hợp sẵn script tạo đường hầm an toàn qua Cloudflare Tunnel:
```bash
# Khởi tạo Public URL trực tiếp ra ngoài Internet
python deploy_tunnel.py
```
Script sẽ cung cấp một đường link dạng:
`https://[subdomain].trycloudflare.com` — Có thể truy cập tức thì từ bất kỳ thiết bị nào (Laptop, Điện thoại, Máy tính bảng).
