import json
import uuid
from datetime import datetime, timedelta
from .database import db_session
from .auth import hash_password
from .services.matching_engine import calculate_match

def seed_database():
    with db_session() as conn:
        cursor = conn.cursor()
        now = datetime.now()
        default_pwd = hash_password("password123")

        print("🌱 Seeding comprehensive multi-industry data for CareerBridge AI...")

        # 1. Users
        users_data = [
            # Admin
            ("usr_admin01", "admin@careerbridge.edu.vn", default_pwd, "PGS. TS. Trần Đức Thịnh", "admin", "0901234567", "Đại học Quốc gia TP.HCM", "Trung tâm Hướng nghiệp & Việc làm", 2015, "Giám đốc Trung tâm Hướng nghiệp Sinh viên."),
            
            # Recruiters across Industries
            ("usr_rec01", "recruiter@careerbridge.edu.vn", default_pwd, "Chị Lê Mai Anh (HR Manager)", "recruiter", "0912345678", "FPT Software Talent Acquisition", "Bộ phận Nhân sự & Tuyển dụng", 2018, "Trưởng ban tuyển dụng tài năng trẻ FPT Software."),
            ("usr_rec02", "recruiter2@careerbridge.edu.vn", default_pwd, "Anh Vũ Hoàng Nam (Tech Lead)", "recruiter", "0923456789", "VNG Corporation - Zalo AI", "Bộ phận AI & Cloud", 2016, "Tìm kiếm các bạn sinh viên đam mê AI và hệ thống phân tán."),
            ("usr_rec03", "recruiter3@careerbridge.edu.vn", default_pwd, "Chị Đỗ Ngọc Linh (Recruitment Specialist)", "recruiter", "0934567890", "Viettel Digital Services", "Trung tâm Phát triển Phần mềm", 2019, "Tuyển dụng kỹ sư số trẻ cho các nền tảng Viettel Money."),
            ("usr_rec04", "recruiter4@careerbridge.edu.vn", default_pwd, "Chị Nguyễn Hải Yến (Marketing Director)", "recruiter", "0941122334", "Unilever & Shopee Brand Hub", "Bộ phận Tiếp thị & Truyền thông", 2017, "Tìm kiếm các tài năng trẻ sáng tạo trong lĩnh vực Digital Marketing."),
            ("usr_rec05", "recruiter5@careerbridge.edu.vn", default_pwd, "Anh Đặng Quốc Bảo (Head of Investment)", "recruiter", "0952233445", "Techcombank & SSI Securities", "Khối Ngân hàng Bán buôn & Phân tích", 2015, "Săn đón chuyên viên phân tích tài chính và định giá xuất sắc."),
            ("usr_rec06", "recruiter6@careerbridge.edu.vn", default_pwd, "Chị Hoàng Minh Phương (Senior HR BP)", "recruiter", "0963344556", "VinFast Auto HR Center", "Khối Nhân sự Tập đoàn", 2018, "Phát triển đội ngũ nhân tài trẻ phục vụ chiến lược toàn cầu của VinFast."),
            ("usr_rec07", "recruiter7@careerbridge.edu.vn", default_pwd, "Anh Ngô Tuấn Kiệt (Supply Chain Director)", "recruiter", "0974455667", "DHL Global Forwarding Vietnam", "Bộ phận Vận hành & Logistics", 2016, "Kết nối nhân tài chuỗi cung ứng với mạng lưới logistics toàn cầu."),
            ("usr_rec08", "recruiter8@careerbridge.edu.vn", default_pwd, "Chị Phan Bảo Trâm (Lead Product Designer)", "recruiter", "0985566778", "MoMo Fintech Product Studio", "Khối Trải nghiệm Người dùng UI/UX", 2019, "Kiến tạo trải nghiệm tài chính tiện lợi hàng đầu cho hàng chục triệu người Việt."),

            # Students across Diverse Disciplines
            # IT / Backend
            ("usr_stu01", "student@careerbridge.edu.vn", default_pwd, "Nguyễn Minh Quân", "student", "0945678901", "Đại học Bách Khoa", "Khoa Khoa học và Kỹ thuật Máy tính", 2026, "Sinh viên năm cuối đam mê Backend và kiến trúc microservices."),
            # Business Intelligence / Data
            ("usr_stu02", "ha.tran@student.edu.vn", default_pwd, "Trần Thị Thu Hà", "student", "0956789012", "Đại học Kinh tế - Luật", "Khoa Hệ thống Thông tin Kinh tế", 2026, "Yêu thích phân tích dữ liệu kinh doanh (BI & Data Analytics), triển khai dashboard Power BI."),
            # Frontend
            ("usr_stu03", "long.le@student.edu.vn", default_pwd, "Lê Hoàng Long", "student", "0967890123", "Đại học Công nghệ Thông tin", "Khoa Kỹ thuật Phần mềm", 2027, "Sinh viên năm 3 chuyên sâu Frontend hiện đại (React, TypeScript, Next.js, Tailwind)."),
            # AI / Machine Learning
            ("usr_stu04", "bao.pham@student.edu.vn", default_pwd, "Phạm Gia Bảo", "student", "0978901234", "Đại học Khoa học Tự nhiên", "Khoa Trí tuệ Nhân tạo", 2026, "GPA 3.82/4.0. Giải Nghiên cứu Khoa học sinh viên cấp trường với đề tài RAG và NLP tiếng Việt."),
            
            # Digital Marketing & Media
            ("usr_stu05", "my.hoang@student.edu.vn", default_pwd, "Hoàng Thảo My", "student", "0981234561", "Đại học Ngoại thương (FTU)", "Khoa Quản trị Kinh doanh Quốc tế - Marketing", 2026, "Đam mê Digital Marketing, Performance Ads và sáng tạo nội dung đa kênh. Đã quản lý ngân sách quảng cáo hơn 150 triệu VNĐ với ROAS 4.8x."),
            
            # Finance & Banking
            ("usr_stu06", "minh.do@student.edu.vn", default_pwd, "Đỗ Hoàng Minh", "student", "0981234562", "Đại học Kinh tế Quốc dân (NEU)", "Khoa Tài chính - Ngân hàng", 2026, "GPA 3.72/4.0. Ứng viên CFA Level 1. Thành thạo xây dựng mô hình tài chính 3 báo cáo và định giá DCF."),
            
            # Logistics & Supply Chain
            ("usr_stu07", "trong.vu@student.edu.vn", default_pwd, "Vũ Đình Trọng", "student", "0981234563", "Đại học Giao thông Vận tải", "Khoa Quản trị Chuỗi Cung ứng & Logistics", 2026, "Nắm chắc Incoterms 2020, quy trình khai báo hải quan điện tử VNACCS và hoạch định tồn kho an toàn."),
            
            # HR & Talent Acquisition
            ("usr_stu08", "phuong.bui@student.edu.vn", default_pwd, "Bùi Mai Phương", "student", "0981234564", "Đại học Kinh tế TP.HCM (UEH)", "Khoa Quản trị Nguồn Nhân lực", 2026, "Thực tập sinh HR năng động, đam mê săn tìm nhân tài công nghệ và tối ưu hóa trải nghiệm ứng viên."),
            
            # UI/UX & Product Design
            ("usr_stu09", "khoa.ly@student.edu.vn", default_pwd, "Lý Anh Khoa", "student", "0981234565", "Đại học Kiến trúc TP.HCM", "Khoa Thiết kế Mỹ thuật Công nghiệp & UI/UX", 2026, "Đam mê xây dựng Design System và thiết kế giao diện lấy người dùng làm trung tâm trên Figma."),
            
            # Automation & Robotics
            ("usr_stu10", "huy.tran@student.edu.vn", default_pwd, "Trần Quốc Huy", "student", "0981234566", "Đại học Bách Khoa", "Khoa Cơ điện tử & Tự động hóa", 2026, "Thành thạo lập trình PLC Siemens S7-1200, thiết kế mạch điện công nghiệp và cánh tay robot SCARA.")
        ]

        for u in users_data:
            cursor.execute("""
                INSERT OR IGNORE INTO users (id, email, hashed_password, full_name, role, phone, university, major, graduation_year, bio, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (*u, (now - timedelta(days=25)).isoformat()))

        # 2. Student Profiles
        profiles_data = [
            ("usr_stu01", 3.52, 
             ["Python", "FastAPI", "SQL", "PostgreSQL", "Docker", "Git", "RESTful APIs", "Redis"],
             ["Backend Developer", "Software Engineer"],
             ["Công nghệ thông tin & Phần mềm", "Thương mại điện tử & Fintech"],
             ["Tiếng Việt (Bản ngữ)", "Tiếng Anh (IELTS 7.0)"],
             ["AWS Certified Cloud Practitioner", "PostgreSQL Associate"],
             "Họ và tên: Nguyễn Minh Quân\nEmail: student@careerbridge.edu.vn | GitHub: github.com/minhquan-dev\n\nMỤC TIÊU NGHỀ NGHIỆP: Trở thành Kỹ sư Backend xuất sắc.\nHỌC VẤN: Đại học Bách Khoa (2022 - 2026) - Khoa học Máy tính. GPA: 3.52/4.0.\nKỸ NĂNG: Python, FastAPI, SQL, PostgreSQL, Docker, Redis.\nDỰ ÁN: Nền tảng đặt xe thông minh EcoRide với thời gian phản hồi API dưới 120ms."),
            
            ("usr_stu02", 3.65,
             ["SQL", "Python", "Pandas", "Power BI", "Tableau", "Excel", "Data Visualization", "Machine Learning"],
             ["Data Analyst", "Business Intelligence Specialist"],
             ["Thương mại điện tử & Fintech", "Tài chính, Ngân hàng & Chứng khoán"],
             ["Tiếng Việt (Bản ngữ)", "Tiếng Anh (TOEIC 850)"],
             ["Microsoft Power BI Data Analyst Associate (PL-300)", "Google Data Analytics Certificate"],
             "Họ và tên: Trần Thị Thu Hà\nEmail: ha.tran@student.edu.vn\nHỌC VẤN: Đại học Kinh tế - Luật - HTTT Quản lý. GPA: 3.65/4.0.\nKỸ NĂNG: Power BI, Tableau, SQL nâng cao, Python Pandas.\nDỰ ÁN: Dashboard phân tích doanh số và hành vi tiêu dùng chuỗi 50 siêu thị."),

            ("usr_stu03", 3.28,
             ["JavaScript", "TypeScript", "React.js", "Tailwind CSS", "HTML5/CSS3", "Next.js", "Git", "Figma"],
             ["Frontend Developer", "Web Developer"],
             ["Công nghệ thông tin & Phần mềm"],
             ["Tiếng Việt (Bản ngữ)", "Tiếng Anh (Giao tiếp tốt)"],
             ["Meta Front-End Developer Professional Certificate"],
             "Họ và tên: Lê Hoàng Long\nEmail: long.le@student.edu.vn | Portfolio: lehoanglong.dev\nHỌC VẤN: Đại học Công nghệ Thông tin - Kỹ thuật Phần mềm. GPA: 3.28/4.0.\nKỸ NĂNG: React.js, Next.js, Tailwind CSS, TypeScript.\nDỰ ÁN: Giao diện sàn TMĐT TechStore đạt điểm hiệu năng Google Lighthouse 95+."),

            ("usr_stu04", 3.82,
             ["Python", "PyTorch", "Scikit-Learn", "Deep Learning", "NLP", "LLM", "RAG", "Docker", "Git"],
             ["AI / Machine Learning Engineer", "Data Scientist"],
             ["Trí tuệ nhân tạo & Dữ liệu", "Công nghệ thông tin & Phần mềm"],
             ["Tiếng Việt (Bản ngữ)", "Tiếng Anh (IELTS 7.5)"],
             ["DeepLearning.AI Machine Learning Specialization"],
             "Họ và tên: Phạm Gia Bảo\nEmail: bao.pham@student.edu.vn | GitHub: github.com/giabao-ai\nHỌC VẤN: Đại học Khoa học Tự nhiên - Trí tuệ Nhân tạo. GPA: 3.82/4.0.\nKỸ NĂNG: PyTorch, NLP, LangChain, RAG, HuggingFace.\nDỰ ÁN: Mô hình RAG tra cứu văn bản pháp luật tiếng Việt với độ chính xác 91.2%."),

            # Student 5: Marketing
            ("usr_stu05", 3.65,
             ["Google Ads", "Meta Ads", "SEO", "Content Marketing", "Google Analytics (GA4)", "Canva", "TikTok Ads", "Copywriting"],
             ["Digital Marketing & Performance Media", "Content Strategist"],
             ["Digital Marketing & Truyền thông", "Thương mại điện tử & Fintech"],
             ["Tiếng Việt (Bản ngữ)", "Tiếng Anh (IELTS 7.5)"],
             ["Google Ads Search Certification (2025)", "HubSpot Inbound Marketing"],
             "Họ và tên: Hoàng Thảo My\nEmail: my.hoang@student.edu.vn | Portfolio: myhoang-marketing.vn\n\nMỤC TIÊU NGHỀ NGHIỆP:\nTrở thành Chuyên viên Digital Marketing hàng đầu, tối ưu hóa hiệu quả chuyển đổi và lan tỏa giá trị thương hiệu.\n\nHỌC VẤN:\n- Đại học Ngoại thương (2022 - 2026) - Chuyên ngành Marketing. GPA: 3.65/4.0.\n\nKỸ NĂNG CHÍNH:\n- Chạy quảng cáo đa kênh: Google Ads (Search, Performance Max), Meta Ads, TikTok Ads.\n- Đo lường & Tối ưu: Google Analytics 4 (GA4), Phễu chuyển đổi CRO, ROAS, A/B Testing.\n- Sáng tạo nội dung: Xây dựng Content Pillar, Copywriting, Thiết kế hình ảnh bằng Canva.\n\nCHIẾN DỊCH TIÊU BIỂU:\n1. Chiến dịch Ra mắt Dòng mỹ phẩm Thiên nhiên EcoGlow:\n- Lập kế hoạch phân bổ ngân sách 120 triệu đồng trên Facebook và TikTok Ads.\n- Đạt chỉ số ROAS 4.8x và thu hút hơn 8.500 khách hàng tiềm năng trong 3 tuần.\n2. Phát triển Kênh TikTok thương hiệu sinh viên:\n- Đạt 150.000 người theo dõi và hơn 2.5 triệu lượt xem video tự nhiên (Organic Reach)."),

            # Student 6: Finance
            ("usr_stu06", 3.72,
             ["Financial Modeling", "Báo cáo Tài chính", "Excel Advanced", "Định giá Doanh nghiệp (DCF)", "Phân tích Ngành", "Corporate Finance", "Power BI"],
             ["Financial Analyst & Phân tích Tài chính", "Chuyên viên Phân tích Đầu tư"],
             ["Tài chính, Ngân hàng & Chứng khoán"],
             ["Tiếng Việt (Bản ngữ)", "Tiếng Anh (IELTS 7.5)"],
             ["CFA Investment Foundations Program", "FMVA Financial Modeling Certification"],
             "Họ và tên: Đỗ Hoàng Minh\nEmail: minh.do@student.edu.vn | LinkedIn: linkedin.com/in/minhdo-finance\n\nMỤC TIÊU NGHỀ NGHIỆP:\nPhát triển sự nghiệp trong lĩnh vực Phân tích Tài chính và Thẩm định Đầu tư tại các định chế tài chính uy tín.\n\nHỌC VẤN:\n- Đại học Kinh tế Quốc dân (2022 - 2026) - Chuyên ngành Tài chính Doanh nghiệp. GPA: 3.72/4.0 (Top 5% ngành).\n\nKỸ NĂNG:\n- Xây dựng mô hình tài chính 3 báo cáo liên kết (Financial Modeling 3-Statement).\n- Định giá doanh nghiệp theo phương pháp Chiết khấu Dòng tiền (DCF) và Phương pháp So sánh (P/E, P/B, EV/EBITDA).\n- Sử dụng thành thạo Excel VBA, Power BI và truy xuất dữ liệu Bloomberg/FiinPro.\n\nDỰ ÁN THỰC CHIẾN:\n- Báo cáo phân tích chuyên sâu ngành Năng lượng Tái tạo tại Việt Nam, dự phóng dòng tiền và định giá 3 doanh nghiệp đầu ngành với khuyến nghị MUA chính xác trước sóng tăng 24%.\n- Giải Nhì cuộc thi Phân tích Đầu tư Tài chính Sinh viên Toàn quốc năm 2025."),

            # Student 7: Logistics & Supply Chain
            ("usr_stu07", 3.48,
             ["Incoterms 2020", "Thủ tục Hải quan", "Quản lý Kho (WMS)", "Vận tải Đa phương thức", "ERP/SAP Basics", "Excel Advanced", "Logistics Operations"],
             ["Supply Chain & Quản trị Chuỗi Cung ứng (Logistics)", "Logistics Coordinator"],
             ["Logistics & Quản trị Chuỗi cung ứng"],
             ["Tiếng Việt (Bản ngữ)", "Tiếng Anh (TOEIC 820)"],
             ["FIATA Diploma in Freight Forwarding Foundation", "Chứng chỉ Khai báo Hải quan Điện tử"],
             "Họ và tên: Vũ Đình Trọng\nEmail: trong.vu@student.edu.vn | SĐT: 0981234563\n\nHỌC VẤN:\n- Đại học Giao thông Vận tải (2022 - 2026) - Chuyên ngành Quản trị Chuỗi Cung ứng. GPA: 3.48/4.0.\n\nKỸ NĂNG:\n- Thành thạo các điều kiện thương mại quốc tế Incoterms 2020 (FOB, CIF, CFR, DDP).\n- Quy trình thông quan xuất nhập khẩu trên hệ thống VNACCS/VCIS.\n- Quản lý vận hành kho bãi (FIFO, LIFO, tính toán tồn kho an toàn Safety Stock).\n\nDỰ ÁN:\n- Đề án Tối ưu hóa lộ trình giao nhận hàng chặng cuối (Last-mile delivery) cho đơn vị chuyển phát nhanh, giúp giảm 14% chi phí nhiên liệu và rút ngắn 22% thời gian giao hàng."),

            # Student 8: HR
            ("usr_stu08", 3.58,
             ["Quy trình Tuyển dụng", "Phỏng vấn STAR", "Luật Lao động", "Xây dựng Thương hiệu Tuyển dụng", "Đánh giá KPIs", "Onboarding", "Excel"],
             ["HR & Quản trị Nhân sự (Talent Acquisition)", "HR Specialist"],
             ["Quản trị Nhân sự (HR)"],
             ["Tiếng Việt (Bản ngữ)", "Tiếng Anh (IELTS 7.0)"],
             ["SHRM Certified HR Foundation", "Chứng chỉ Pháp luật Lao động Thực hành"],
             "Họ và tên: Bùi Mai Phương\nEmail: phuong.bui@student.edu.vn\n\nHỌC VẤN:\n- Đại học Kinh tế TP.HCM (UEH) (2022 - 2026) - Quản trị Nhân lực. GPA: 3.58/4.0.\n\nKỸ NĂNG:\n- Xây dựng phễu tuyển dụng nhân tài, tạo nguồn ứng viên trên LinkedIn, TopCV.\n- Thiết kế bộ câu hỏi phỏng vấn năng lực theo chuẩn STAR.\n- Nắm vững Bộ luật Lao động Việt Nam 2019 về hợp đồng, thử việc và chế độ bảo hiểm.\n\nKINH NGHIỆM:\n- Hỗ trợ tuyển dụng thành công 18 vị trí thực tập sinh kỹ thuật cho CLB Khởi nghiệp sinh viên với tỷ lệ giữ chân sau 6 tháng đạt 92%."),

            # Student 9: UI/UX Design
            ("usr_stu09", 3.60,
             ["Figma Advanced", "User Research", "Wireframing & Prototyping", "Design Systems", "Usability Testing", "UI/UX Design", "Auto Layout"],
             ["UI/UX & Product Designer", "Product Designer"],
             ["Thiết kế Sản phẩm & UI/UX", "Công nghệ thông tin & Phần mềm"],
             ["Tiếng Việt (Bản ngữ)", "Tiếng Anh (IELTS 7.0)"],
             ["Google UX Design Professional Certificate", "Figma Advanced Certification"],
             "Họ và tên: Lý Anh Khoa\nEmail: khoa.ly@student.edu.vn | Portfolio: dribbble.com/anhkhoa-design\n\nHỌC VẤN:\n- Đại học Kiến trúc TP.HCM (2022 - 2026) - Thiết kế Đồ họa & UI/UX. GPA: 3.60/4.0.\n\nKỸ NĂNG:\n- Thiết kế Component chuẩn Design System trên Figma (Auto Layout, Variants, Variables).\n- Thực hiện User Interview, xây dựng User Persona và Customer Journey Map.\n- Kiểm thử tính khả dụng (Usability Testing) và đo lường chỉ số SUS (System Usability Scale).\n\nDỰ ÁN:\n- Thiết kế lại trải nghiệm ứng dụng Quản lý Chi tiêu Sinh viên SmartSpend, nâng cao tỷ lệ hoàn thành tác vụ nạp tiền lên 94%."),

            # Student 10: Automation
            ("usr_stu10", 3.55,
             ["Lập trình PLC", "AutoCAD Electrical", "SCADA & HMI", "Cảm biến Công nghiệp", "Robotics", "C/C++", "Điện công nghiệp"],
             ["Kỹ sư Tự động hóa & Cơ điện tử (Automation & Robotics)"],
             ["Kỹ thuật & Tự động hóa"],
             ["Tiếng Việt (Bản ngữ)", "Tiếng Anh (TOEIC 780)"],
             ["Siemens Certified Automation Associate (TIA Portal)", "AutoCAD Certified Professional"],
             "Họ và tên: Trần Quốc Huy\nEmail: huy.tran@student.edu.vn | SĐT: 0981234566\n\nHỌC VẤN:\n- Đại học Bách Khoa (2022 - 2026) - Cơ điện tử & Tự động hóa. GPA: 3.55/4.0.\n\nKỸ NĂNG:\n- Lập trình PLC Siemens S7-1200 / S7-1500 bằng ngôn ngữ Ladder (LAD) và Structured Control Language (SCL).\n- Thiết kế giao diện giám sát SCADA/HMI trên WinCC.\n- Thiết kế bản vẽ sơ đồ nguyên lý mạch điện điều khiển động cơ trên AutoCAD Electrical.\n\nDỰ ÁN:\n- Chế tạo mô hình Dây chuyền Phân loại và Đóng gói Sản phẩm tự động sử dụng cảm biến màu sắc và cánh tay robot, đạt giải Nhất Hội nghị Sinh viên Nghiên cứu Khoa học Khoa Cơ khí 2025.")
        ]

        for p in profiles_data:
            cursor.execute("""
                INSERT OR REPLACE INTO student_profiles (
                    user_id, gpa, skills, dream_roles, target_industries,
                    languages, certifications, cv_text, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                p[0], p[1], json.dumps(p[2]), json.dumps(p[3]), json.dumps(p[4]),
                json.dumps(p[5]), json.dumps(p[6]), p[7], now.isoformat()
            ))

        # 3. Job Postings across all Sectors
        jobs_data = [
            # IT & Software
            ("job_01", "usr_rec02", "Thực tập sinh Kỹ sư Trí tuệ Nhân tạo (AI Intern)", "VNG Corporation - Zalo AI",
             "TP. Hồ Chí Minh (Hybrid)", "Thực tập sinh (Internship)", "8.000.000 - 12.000.000 VNĐ",
             "Tham gia đội ngũ nghiên cứu và phát triển các mô hình AI tiếng Việt thế hệ mới tại Zalo AI Lab.",
             "- Sinh viên năm 3, năm cuối chuyên ngành CNTT, Khoa học Máy tính, Trí tuệ Nhân tạo.\n- Thành thạo Python, PyTorch hoặc TensorFlow.\n- Nắm vững kiến thức nền tảng về Machine Learning, Deep Learning, NLP hoặc Computer Vision.\n- Điểm GPA từ 3.2 trở lên là lợi thế.",
             "- Nghiên cứu, thử nghiệm và tối ưu hóa các kiến trúc mô hình học sâu.\n- Xử lý và chuẩn hóa tập dữ liệu tiếng Việt quy mô lớn.\n- Phối hợp triển khai mô hình thử nghiệm lên môi trường microservices.",
             ["Python", "PyTorch", "Machine Learning", "Deep Learning", "NLP", "Git"],
             "Trí tuệ nhân tạo & Dữ liệu", 3.2),

            ("job_02", "usr_rec01", "Kỹ sư Lập trình Backend (Fresher / Junior Python)", "FPT Software",
             "Hà Nội / TP. Hồ Chí Minh", "Mới tốt nghiệp (Fresher)", "12.000.000 - 20.000.000 VNĐ",
             "FPT Software mở đợt tuyển dụng Kỹ sư Backend tham gia các dự án chuyển đổi số quốc tế cho khách hàng Nhật Bản và Bắc Mỹ.",
             "- Tốt nghiệp hoặc chuẩn bị tốt nghiệp Đại học ngành CNTT hoặc liên quan.\n- Nắm vững ngôn ngữ Python, có kinh nghiệm với FastAPI hoặc Django.\n- Hiểu biết về cơ sở dữ liệu SQL (PostgreSQL / MySQL) và thiết kế RESTful API.\n- Biết sử dụng Git và Docker là điểm cộng lớn.",
             "- Tham gia phát triển các API dịch vụ cốt lõi của hệ thống doanh nghiệp.\n- Viết Unit Test và tối ưu hiệu năng cơ sở dữ liệu.\n- Tham gia vào các buổi Daily Scrum và Sprint Planning cùng khách hàng.",
             ["Python", "FastAPI", "SQL", "PostgreSQL", "Docker", "Git", "RESTful APIs"],
             "Công nghệ thông tin & Phần mềm", 2.8),

            ("job_03", "usr_rec03", "Thực tập sinh Lập trình Frontend (React.js Intern)", "Viettel Digital Services",
             "Hà Nội (Trực tiếp)", "Thực tập sinh (Internship)", "7.000.000 - 10.000.000 VNĐ",
             "Cơ hội thực chiến tại Trung tâm Sản phẩm số Viettel Money, tham gia xây dựng giao diện ứng dụng cho 25 triệu khách hàng.",
             "- Sinh viên năm 3, 4 có định hướng chuyên sâu về Frontend.\n- Nắm chắc HTML5, CSS3, JavaScript (ES6+).\n- Đã từng thực hành với thư viện React.js, Tailwind CSS hoặc TypeScript trong các bài tập lớn.\n- Yêu thích trải nghiệm người dùng và thiết kế hiện đại.",
             "- Lập trình các linh kiện UI theo thiết kế Figma.\n- Kết nối API với hệ thống Backend.\n- Kiểm thử và tối ưu tốc độ phản hồi trên nhiều kích thước màn hình.",
             ["JavaScript", "React.js", "Tailwind CSS", "HTML5/CSS3", "TypeScript", "Git"],
             "Công nghệ thông tin & Phần mềm", 2.5),

            ("job_04", "usr_rec01", "Chuyên viên Phân tích Dữ liệu (Data Analyst Fresher)", "FPT Software",
             "Đà Nẵng / TP. Hồ Chí Minh", "Mới tốt nghiệp (Fresher)", "11.000.000 - 18.000.000 VNĐ",
             "Tham gia phân tích số liệu vận hành và xây dựng giải pháp Business Intelligence cho tập đoàn đa quốc gia.",
             "- Tốt nghiệp các ngành Hệ thống thông tin, Thống kê, Kinh tế hoặc CNTT.\n- Thành thạo viết truy vấn SQL phức tạp (Join, Window Functions, Aggregate).\n- Có kinh nghiệm trực quan hóa dữ liệu với Power BI hoặc Tableau.\n- Sử dụng được Python (Pandas) để xử lý dữ liệu.",
             "- Xây dựng và duy trì các Dashboard báo cáo chỉ số kinh doanh theo thời gian thực.\n- Làm sạch và chuẩn hóa dữ liệu từ nhiều nguồn khác nhau.\n- Trình bày kết quả phân tích cho các bên liên quan để đưa ra quyết định.",
             ["SQL", "Power BI", "Python", "Pandas", "Tableau", "Excel", "Data Visualization"],
             "Thương mại điện tử & Fintech", 3.0),

            ("job_05", "usr_rec02", "Kỹ sư DevOps / Cloud (Internship & Fresher)", "VNG Corporation - Cloud Team",
             "TP. Hồ Chí Minh", "Thực tập sinh (Internship)", "9.000.000 - 14.000.000 VNĐ",
             "Tham gia vận hành hệ thống đám mây VNG Cloud và các cụm hạ tầng quy mô lớn.",
             "- Sinh viên năm cuối hoặc mới tốt nghiệp ngành Mạng máy tính, CNTT.\n- Sử dụng thành thạo Linux (Ubuntu/CentOS), hiểu biết về mạng căn bản (TCP/IP, DNS, Load Balancer).\n- Biết sử dụng Docker và các công cụ CI/CD (GitHub Actions, GitLab CI).\n- Có tư duy tự động hóa bằng Bash Script hoặc Python.",
             "- Hỗ trợ đóng gói ứng dụng bằng Docker và triển khai lên cụm máy chủ.\n- Thiết lập giám sát cảnh báo với Prometheus và Grafana.\n- Tối ưu hóa quy trình deploy tự động.",
             ["Linux", "Docker", "Git", "Python", "CI/CD", "DevOps"],
             "Công nghệ thông tin & Phần mềm", 2.8),

            ("job_06", "usr_rec03", "Chuyên viên Phân tích Nghiệp vụ (Business Analyst - BA Intern)", "Viettel Digital Services",
             "Hà Nội", "Thực tập sinh (Internship)", "6.000.000 - 9.000.000 VNĐ",
             "Đóng vai trò cầu nối quan trọng giữa khối kinh doanh và đội ngũ kỹ thuật sản phẩm Viettel Digital.",
             "- Sinh viên các ngành Hệ thống thông tin, Quản trị Kinh doanh, CNTT.\n- Kỹ năng giao tiếp và lắng nghe xuất sắc, tư duy logic mạch lạc.\n- Biết vẽ Wireframe/Prototype cơ bản trên Figma và viết User Story theo chuẩn Agile/Scrum.",
             "- Khảo sát và ghi nhận yêu cầu tính năng từ người dùng và đối tác.\n- Viết tài liệu đặc tả nghiệp vụ (SRS, Use Cases, User Flows).\n- Phối hợp cùng QA/QC nghiệm thu tính năng trước khi ra mắt thị trường.",
             ["Business Analysis", "Agile/Scrum", "Figma", "User Stories", "SQL Basics"],
             "Thương mại điện tử & Fintech", 2.8),

            # NEW INDUSTRY 1: Digital Marketing & Media
            ("job_07", "usr_rec04", "Thực tập sinh Tiếp thị Kỹ thuật số (Digital Marketing Intern)", "Unilever Vietnam",
             "TP. Hồ Chí Minh (Quận 7)", "Thực tập sinh (Internship)", "7.500.000 - 10.500.000 VNĐ",
             "Tham gia trực tiếp cùng các Brand Team hàng đầu như OMO, Dove, Lifebuoy trong việc triển khai các chiến dịch truyền thông đa kênh.",
             "- Sinh viên năm 3, 4 các ngành Marketing, Truyền thông, Quản trị Kinh doanh hoặc Ngoại thương.\n- Hiểu biết về các kênh quảng cáo Meta Ads, TikTok Ads, Google Search.\n- Kỹ năng viết bài và sáng tạo nội dung hấp dẫn.\n- Tiếng Anh giao tiếp tốt (IELTS 6.5 trở lên).",
             "- Hỗ trợ lên kế hoạch nội dung (Content Plan) hàng tháng cho các nhãn hàng.\n- Phối hợp cùng Creative Agency sản xuất ấn phẩm truyền thông hình ảnh và video.\n- Theo dõi và tổng hợp báo cáo các chỉ số tương tác (CTR, Engagement, Reach) bằng Google Analytics.",
             ["Google Ads", "Meta Ads", "Content Marketing", "Canva", "SEO", "Google Analytics (GA4)"],
             "Digital Marketing & Truyền thông", 3.0),

            ("job_08", "usr_rec04", "Chuyên viên Tối ưu Hiệu suất Quảng cáo (Performance Media Fresher)", "Shopee Vietnam",
             "TP. Hồ Chí Minh (Quận 1)", "Mới tốt nghiệp (Fresher)", "12.000.000 - 18.000.000 VNĐ",
             "Quản lý ngân sách quảng cáo lớn và tối ưu hóa chỉ số hoàn vốn đầu tư ROAS cho các ngày siêu mua sắm hàng tháng của Shopee.",
             "- Tốt nghiệp Đại học khối ngành Kinh tế, Marketing, Thống kê.\n- Nắm chắc cơ chế đấu thầu quảng cáo trên Facebook Ads, Google Ads và Shopee Ads.\n- Tư duy số liệu nhạy bén, sử dụng thành thạo Excel (VLOOKUP, PivotTable, Data Analysis).\n- Khả năng làm việc dưới áp lực trong các chiến dịch Mega Sale.",
             "- Thiết lập và theo dõi các chiến dịch quảng cáo trả phí (Paid Media) theo thời gian thực.\n- Thực hiện A/B Testing liên tục tiêu đề, hình ảnh và tệp đối tượng mục tiêu.\n- Đề xuất các giải pháp tối ưu chi phí thu hút khách hàng mới (CAC).",
             ["Google Ads", "Meta Ads", "Google Analytics (GA4)", "Excel Advanced", "ROAS Optimization", "A/B Testing"],
             "Digital Marketing & Truyền thông", 3.2),

            # NEW INDUSTRY 2: Finance, Banking & Securities
            ("job_09", "usr_rec05", "Thực tập sinh Phân tích Tài chính Doanh nghiệp (Financial Analyst Intern)", "Techcombank",
             "Hà Nội / TP. Hồ Chí Minh", "Thực tập sinh (Internship)", "8.000.000 - 12.000.000 VNĐ",
             "Cơ hội thực chiến tại Khối Khách hàng Doanh nghiệp quy mô lớn của Techcombank, tham gia đánh giá sức khỏe tài chính của các tập đoàn hàng đầu.",
             "- Sinh viên năm cuối hoặc mới tốt nghiệp ngành Tài chính, Ngân hàng, Kế toán - Kiểm toán.\n- Điểm GPA từ 3.2 trở lên.\n- Nắm vững nguyên lý đọc hiểu và phân tích 3 Báo cáo Tài chính.\n- Thành thạo Excel nâng cao, có định hướng thi chứng chỉ CFA là lợi thế lớn.",
             "- Thu thập số liệu và bóc tách cấu trúc dòng tiền, nợ vay và biên lợi nhuận của doanh nghiệp.\n- Hỗ trợ xây dựng mô hình dự báo tài chính (Financial Projection).\n- Soạn thảo báo cáo đánh giá tín dụng và khả năng trả nợ.",
             ["Financial Modeling", "Báo cáo Tài chính", "Excel Advanced", "Định giá Doanh nghiệp (DCF)", "Corporate Finance"],
             "Tài chính, Ngân hàng & Chứng khoán", 3.2),

            ("job_10", "usr_rec05", "Chuyên viên Phân tích Đầu tư & Nghiên cứu Ngành (Equity Research Analyst)", "SSI Securities",
             "TP. Hồ Chí Minh (Quận 1)", "Mới tốt nghiệp (Fresher)", "15.000.000 - 22.000.000 VNĐ",
             "Gia nhập Công ty Chứng khoán dẫn đầu thị phần Việt Nam, cung cấp các khuyến nghị đầu tư cổ phiếu cho các quỹ đầu tư tổ chức trong và ngoài nước.",
             "- Tốt nghiệp loại Giỏi các trường NEU, FTU, UEH, hoặc du học sinh ngành Tài chính.\n- Kỹ năng xây dựng Financial Model chuẩn mực quốc tế.\n- Khả năng phân tích định tính mô hình kinh doanh và lợi thế cạnh tranh của doanh nghiệp.\n- Tiếng Anh lưu loát để viết báo cáo phân tích chuyên sâu.",
             "- Xây dựng mô hình định giá DCF và P/E cho các doanh nghiệp niêm yết.\n- Thực hiện các buổi khảo sát thực địa và phỏng vấn ban lãnh đạo doanh nghiệp.\n- Xuất bản các báo cáo ngành và ý tưởng đầu tư cổ phiếu định kỳ.",
             ["Financial Modeling", "Định giá Doanh nghiệp (DCF)", "Báo cáo Tài chính", "Excel Advanced", "Phân tích Ngành", "CFA Foundation"],
             "Tài chính, Ngân hàng & Chứng khoán", 3.3),

            # NEW INDUSTRY 3: Auditing & Accounting
            ("job_11", "usr_rec05", "Thực tập sinh Kiểm toán & Tư vấn Thuế (Audit Trainee / Fresher)", "KPMG Vietnam",
             "Hà Nội / TP. Hồ Chí Minh", "Thực tập sinh (Internship)", "7.500.000 - 11.000.000 VNĐ",
             "Trải nghiệm mùa kiểm toán sôi động tại công ty Kiểm toán Big 4, tiếp cận các chuẩn mực kiểm toán quốc tế và hệ thống khách hàng đa dạng.",
             "- Sinh viên năm cuối hoặc mới tốt nghiệp ngành Kiểm toán, Kế toán, Tài chính.\n- Nắm chắc các nguyên tắc hạch toán kế toán và chuẩn mực VAS/IFRS.\n- Cẩn thận, tỉ mỉ với số liệu và tuân thủ đạo đức nghề nghiệp.\n- Ưu tiên ứng viên đang theo học các môn ACCA hoặc CPA.",
             "- Tham gia chứng kiến kiểm kê tiền mặt, hàng tồn kho và tài sản cố định của khách hàng.\n- Kiểm tra chứng từ phát sinh và gửi thư xác nhận số dư công nợ ngân hàng.\n- Hỗ trợ soát xét các phần hành kiểm toán dưới sự hướng dẫn của Senior Auditor.",
             ["Hạch toán Kế toán", "Chuẩn mực Kế toán (VAS/IFRS)", "Luật Thuế GTGT & TNDN", "Excel Chuyên sâu", "Kiểm toán Báo cáo Tài chính"],
             "Kế toán & Kiểm toán", 3.0),

            # NEW INDUSTRY 4: Logistics & Supply Chain
            ("job_12", "usr_rec07", "Điều phối viên Vận hành Chuỗi Cung ứng (Logistics Operations Intern)", "DHL Global Forwarding",
             "TP. Hồ Chí Minh / Bình Dương", "Thực tập sinh (Internship)", "8.000.000 - 11.000.000 VNĐ",
             "Cơ hội làm việc tại tập đoàn Logistics số 1 thế giới, tham gia vận hành luồng hàng hóa quốc tế đường biển và đường hàng không.",
             "- Sinh viên các ngành Kinh tế đối ngoại, Logistics, Quản trị Chuỗi cung ứng.\n- Nắm chắc điều kiện thương mại Incoterms 2020 và chứng từ xuất nhập khẩu (B/L, Invoice, Packing List).\n- Tiếng Anh giao tiếp và đọc hiểu tài liệu quốc tế tốt.\n- Tinh thần trách nhiệm cao và khả năng giải quyết sự cố phát sinh.",
             "- Phối hợp với hãng tàu, đại lý vận chuyển và cơ quan hải quan để thu xếp lịch trình tàu.\n- Theo dõi tình trạng đơn hàng (Track & Trace) và cập nhật cho khách hàng xuất nhập khẩu.\n- Quản lý dữ liệu tồn kho và tối ưu hóa chi phí lưu kho bãi.",
             ["Incoterms 2020", "Thủ tục Hải quan", "Quản lý Kho (WMS)", "Vận tải Đa phương thức", "ERP/SAP Basics"],
             "Logistics & Quản trị Chuỗi cung ứng", 2.8),

            # NEW INDUSTRY 5: Human Resources & Recruitment
            ("job_13", "usr_rec06", "Chuyên viên Tuyển dụng & Thu hút Tài năng (Talent Acquisition Specialist)", "VinFast Auto",
             "Hà Nội / Hải Phòng", "Mới tốt nghiệp (Fresher)", "11.000.000 - 16.000.000 VNĐ",
             "Đồng hành cùng chiến dịch mở rộng quy mô sản xuất xe điện toàn cầu của VinFast, thu hút các kỹ sư và chuyên gia công nghệ xuất sắc.",
             "- Tốt nghiệp Đại học chuyên ngành Quản trị Nhân sự, Kinh tế, Ngoại ngữ hoặc Luật.\n- Kỹ năng giao tiếp xuất sắc, biết lắng nghe và tạo thiện cảm với ứng viên.\n- Hiểu biết về các kênh tuyển dụng hiện đại (LinkedIn Recruiter, Job Fair, Headhunting).\n- Nắm vững các quy định của Bộ luật Lao động Việt Nam.",
             "- Lập kế hoạch đăng tin tuyển dụng và tìm kiếm chủ động ứng viên tiềm năng.\n- Sàng lọc CV và tiến hành phỏng vấn sơ loại ứng viên theo mô hình STAR.\n- Tổ chức các sự kiện ngày hội việc làm và chương trình hợp tác với các trường đại học.",
             ["Quy trình Tuyển dụng", "Phỏng vấn STAR", "Luật Lao động", "Xây dựng Thương hiệu Tuyển dụng", "Đánh giá KPIs"],
             "Quản trị Nhân sự (HR)", 3.0),

            # NEW INDUSTRY 6: Product Design & UI/UX
            ("job_14", "usr_rec08", "Thực tập sinh Thiết kế Trải nghiệm Sản phẩm (UI/UX Product Designer)", "MoMo E-Wallet",
             "TP. Hồ Chí Minh (Quận 7)", "Thực tập sinh (Internship)", "8.500.000 - 13.000.000 VNĐ",
             "Tham gia đội ngũ thiết kế sản phẩm tài chính số MoMo, nơi mỗi màn hình thiết kế của bạn sẽ chạm đến trải nghiệm của hơn 30 triệu người dùng.",
             "- Sinh viên hoặc mới tốt nghiệp các ngành Thiết kế Đồ họa, Mỹ thuật Công nghiệp, CNTT.\n- Thành thạo công cụ Figma (Auto Layout, Variants, Component, Smart Animate).\n- Có portfolio thể hiện tư duy giải quyết vấn đề và quy trình User Research rõ ràng.\n- Nhạy bén với xu hướng thiết kế giao diện hiện đại và tính khả dụng (Usability).",
             "- Phối hợp với Product Manager và Kỹ sư để vẽ Wireframe, User Flow và Prototype tương tác.\n- Thực hiện các buổi phỏng vấn người dùng và đo lường sự hài lòng trải nghiệm.\n- Đóng góp vào việc duy trì và mở rộng Design System của MoMo.",
             ["Figma Advanced", "User Research", "Wireframing & Prototyping", "Design Systems", "Usability Testing"],
             "Thiết kế Sản phẩm & UI/UX", 3.0),

            # NEW INDUSTRY 7: Automation & Robotics
            ("job_15", "usr_rec06", "Kỹ sư Tự động hóa & Dây chuyền Robot (Automation Engineer)", "VinFast Robotics Complex",
             "Hải Phòng (Hỗ trợ Ký túc xá)", "Mới tốt nghiệp (Fresher)", "14.000.000 - 22.000.000 VNĐ",
             "Vận hành và tối ưu hóa tổ hợp nhà máy sản xuất xe điện tự động hóa 95% với hơn 1.200 robot hàn và sơn ABB/KUKA.",
             "- Tốt nghiệp Đại học các ngành Kỹ thuật Điều khiển & Tự động hóa, Cơ điện tử, Điện - Điện tử.\n- Thành thạo lập trình PLC (Siemens TIA Portal, Mitsubishi hoặc Omron).\n- Đọc hiểu bản vẽ mạch điện công nghiệp và thủy lực khí nén trên AutoCAD.\n- Tinh thần kỷ luật và tuân thủ nghiêm ngặt an toàn lao động.",
             "- Lập trình và hiệu chỉnh chu trình hoạt động của các trạm robot tự động.\n- Giám sát thông số vận hành trên hệ thống SCADA/HMI và xử lý sự cố lỗi dừng máy.\n- Đề xuất các cải tiến Kaizen nhằm nâng cao năng suất dây chuyền.",
             ["Lập trình PLC", "AutoCAD Electrical", "SCADA & HMI", "Cảm biến Công nghiệp", "Robotics"],
             "Kỹ thuật & Tự động hóa", 3.0),

            # NEW INDUSTRY 8: Cybersecurity
            ("job_16", "usr_rec03", "Kỹ sư An toàn Thông tin & Giám sát SOC (Cybersecurity Fresher)", "Viettel Cyber Security",
             "Hà Nội", "Mới tốt nghiệp (Fresher)", "13.000.000 - 20.000.000 VNĐ",
             "Tham gia Trung tâm Giám sát và Phản ứng Sự cố An toàn Thông tin quốc gia (SOC), bảo vệ các hạ tầng số trọng yếu.",
             "- Tốt nghiệp ngành An toàn Thông tin, Mạng máy tính, CNTT.\n- Nắm vững kiến thức về kiến trúc mạng, giao thức TCP/IP và hệ điều hành Linux.\n- Hiểu biết về các lỗ hổng OWASP Top 10 và phương thức tấn công phổ biến.\n- Có chứng chỉ bảo mật quốc tế (CompTIA Security+, CEH, CCNA) là lợi thế lớn.",
             "- Giám sát và phân tích các cảnh báo an ninh mạng trên hệ thống SIEM.\n- Phối hợp điều tra nguyên nhân và cô lập các mối đe dọa mã độc.\n- Rà soát lỗ hổng định kỳ cho các máy chủ và ứng dụng dịch vụ.",
             ["Network Security", "Linux Hardening", "Wireshark", "OWASP Top 10", "Python/Bash", "SOC Monitoring"],
             "An toàn thông tin & Mạng máy tính", 3.0),

            # NEW INDUSTRY 9: Mobile App Development
            ("job_17", "usr_rec02", "Kỹ sư Lập trình Ứng dụng Di động (Flutter / React Native Fresher)", "VNG Corporation - Zalo Mobile",
             "TP. Hồ Chí Minh", "Mới tốt nghiệp (Fresher)", "13.000.000 - 21.000.000 VNĐ",
             "Xây dựng các tính năng mới trên ứng dụng nhắn tin và tiện ích Zalo phục vụ hàng chục triệu người dùng hoạt động mỗi ngày.",
             "- Tốt nghiệp hoặc sinh viên năm cuối ngành CNTT, Kỹ thuật Phần mềm.\n- Có kinh nghiệm phát triển ứng dụng di động với Flutter/Dart hoặc React Native.\n- Hiểu biết về vòng đời ứng dụng, quản lý state (Bloc, Provider, Redux) và kết nối REST API.\n- Chú trọng đến độ mượt mà của hiệu ứng chuyển động (60 FPS) và tối ưu dung lượng bộ nhớ.",
             "- Phát triển các màn hình tính năng mới theo thiết kế UI/UX.\n- Tối ưu hóa hiệu năng render và xử lý lưu trữ dữ liệu ngoại tuyến (Offline Storage).\n- Khắc phục lỗi và tối ưu trải nghiệm trên các dòng điện thoại Android và iOS khác nhau.",
             ["Flutter / Dart", "React Native", "REST API Integration", "Git", "State Management (Bloc/Riverpod)"],
             "Công nghệ thông tin & Phần mềm", 3.0)
        ]

        for j in jobs_data:
            cursor.execute("""
                INSERT OR REPLACE INTO job_postings (
                    id, recruiter_id, title, company_name, location, job_type,
                    salary_range, description, requirements, responsibilities,
                    required_skills, industry, min_gpa, is_active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            """, (
                j[0], j[1], j[2], j[3], j[4], j[5], j[6], j[7], j[8], j[9],
                json.dumps(j[10]), j[11], j[12], (now - timedelta(days=10)).isoformat()
            ))

        # 4. Seed Applications across Multiple Industries
        apps_data = [
            ("app_01", "job_02", "usr_stu01", "applied", "Kính gửi FPT Software, em là Nguyễn Minh Quân, sinh viên năm cuối ĐHBK. Với thế mạnh về Python, FastAPI và Docker, em tin mình sẽ đóng góp tốt cho dự án."),
            ("app_02", "job_01", "usr_stu04", "interview_scheduled", "Em đã có các nghiên cứu thực tế về NLP và Deep Learning tại phòng thí nghiệm trường, rất mong được thử sức tại Zalo AI."),
            ("app_03", "job_04", "usr_stu02", "accepted", "Em đã hoàn thành chứng chỉ PL-300 của Microsoft và có sản phẩm Dashboard thực tế. Rất vinh dự được gia nhập đội ngũ FPT Software."),
            ("app_04", "job_03", "usr_stu03", "reviewing", "Em gửi kèm link portfolio cá nhân lehoanglong.dev với các dự án React và TypeScript."),
            # New cross-industry applications
            ("app_05", "job_07", "usr_stu05", "interview_scheduled", "Em đã từng quản lý chiến dịch quảng cáo TikTok và Meta Ads với ROAS 4.8x. Em rất mong muốn mang nhiệt huyết và tư duy số liệu đến với Unilever."),
            ("app_06", "job_09", "usr_stu06", "accepted", "Em là ứng viên CFA Level 1 với GPA 3.72/4.0. Đã thành thạo lập mô hình tài chính 3 báo cáo và định giá DCF."),
            ("app_07", "job_12", "usr_stu07", "applied", "Em có chứng chỉ Khai báo Hải quan và nắm vững Incoterms 2020. Rất mong muốn được đóng góp cho mạng lưới vận hành DHL."),
            ("app_08", "job_13", "usr_stu08", "reviewing", "Em đã có kinh nghiệm tuyển dụng 18 nhân sự kỹ thuật bằng mô hình phỏng vấn STAR, rất mong muốn gia nhập VinFast."),
            ("app_09", "job_14", "usr_stu09", "interview_scheduled", "Em xin gửi kèm link Dribbble Portfolio các dự án thiết kế Design System và Mobile App tài chính cho MoMo xem xét."),
            ("app_10", "job_15", "usr_stu10", "applied", "Em đã đạt giải Nhất NCKH với đề tài mô hình dây chuyền phân loại tự động sử dụng PLC Siemens S7-1200.")
        ]

        for app in apps_data:
            cursor.execute("SELECT * FROM student_profiles WHERE user_id = ?", (app[2],))
            p_dict = dict(cursor.fetchone())
            cursor.execute("SELECT * FROM users WHERE id = ?", (app[2],))
            u_dict = dict(cursor.fetchone())
            cursor.execute("SELECT * FROM job_postings WHERE id = ?", (app[1],))
            j_dict = dict(cursor.fetchone())

            match_res = calculate_match(p_dict, u_dict, j_dict)
            cursor.execute("""
                INSERT OR REPLACE INTO applications (id, job_id, student_id, match_score, match_analysis, cover_note, status, applied_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                app[0], app[1], app[2], match_res["match_score"],
                json.dumps(match_res), app[4], app[3],
                (now - timedelta(days=4)).isoformat()
            ))

        # 5. Activity logs
        logs = [
            ("log_01", "usr_stu01", "APPLY_JOB", "Ứng tuyển vị trí Kỹ sư Lập trình Backend tại FPT Software"),
            ("log_02", "usr_stu04", "MOCK_INTERVIEW", "Hoàn thành phiên phỏng vấn thử Kỹ sư Trí tuệ Nhân tạo - Điểm 9.2/10"),
            ("log_03", "usr_stu05", "CV_REVIEW", "Chấm điểm ATS hồ sơ Digital Marketing đạt 94/100 điểm"),
            ("log_04", "usr_stu06", "ROADMAP", "Khởi tạo lộ trình kỹ năng Chuyên viên Phân tích Tài chính"),
            ("log_05", "usr_rec05", "SCHEDULE_INTERVIEW", "Mời ứng viên Đỗ Hoàng Minh tham gia phỏng vấn vị trí Financial Analyst"),
            ("log_06", "usr_rec04", "ACCEPT_CANDIDATE", "Gửi thư mời nhận việc (Offer) tới ứng viên Hoàng Thảo My"),
            ("log_07", "usr_admin01", "SYSTEM_AUDIT", "Báo cáo thị trường đa ngành: Đã kết nối thành công 10 lĩnh vực trọng điểm")
        ]
        for l in logs:
            cursor.execute("""
                INSERT OR IGNORE INTO activity_logs (id, user_id, action, details, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (*l, now.isoformat()))

        print("✅ Multi-industry database seeded successfully: 18 users, 10 profiles, 17 jobs across 10 industries, 10 applications.")
