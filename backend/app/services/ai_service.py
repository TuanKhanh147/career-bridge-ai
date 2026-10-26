import re
import json
import httpx
from typing import Dict, Any, List
from ..config import GEMINI_API_KEY, OPENAI_API_KEY

ROLE_SKILL_TAXONOMY = {
    "AI / Machine Learning Engineer": {
        "core": ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "Data Preprocessing", "Linear Algebra", "Git"],
        "advanced": ["MLOps", "Docker", "HuggingFace", "FastAPI", "Vector DBs", "RAG", "Cloud (GCP/AWS)"],
        "soft": ["Problem Solving", "Research Mindset", "Data Storytelling"],
        "keywords": ["model deployment", "inference latency", "precision/recall", "feature engineering", "fine-tuning", "loss function"]
    },
    "Backend Developer": {
        "core": ["Python/FastAPI", "Node.js/Express", "Java/Spring", "SQL & Database Design", "RESTful APIs", "Git"],
        "advanced": ["Docker", "Redis", "Message Queues (Kafka/RabbitMQ)", "Microservices", "CI/CD", "AWS/Cloud"],
        "soft": ["System Design", "Debugging", "Team Collaboration"],
        "keywords": ["throughput", "concurrency", "indexing", "authentication", "api design", "unit testing", "scalability"]
    },
    "Frontend Developer": {
        "core": ["HTML5/CSS3", "JavaScript (ES6+)", "React.js/Vue.js", "Tailwind CSS", "Git", "Responsive Design"],
        "advanced": ["Next.js/TypeScript", "State Management (Redux/Zustand)", "Web Performance Optimization", "SEO", "Testing (Jest/Cypress)"],
        "soft": ["UI/UX Sense", "Communication", "Attention to Detail"],
        "keywords": ["component reusability", "lighthouse score", "lazy loading", "cross-browser compatibility", "design system"]
    },
    "Mobile App Developer": {
        "core": ["Flutter / Dart", "React Native", "Swift / iOS", "Kotlin / Android", "REST API Integration", "Git"],
        "advanced": ["State Management (Bloc/Riverpod/Redux)", "App Store / Google Play Deployment", "Push Notifications", "Offline Storage", "Firebase"],
        "soft": ["User-Centric Mindset", "Performance Tuning", "Cross-Platform Optimization"],
        "keywords": ["hot reload", "native bridge", "widget lifecycle", "app store guidelines", "memory leak", "framerate"]
    },
    "Cybersecurity / An toàn Thông tin": {
        "core": ["Network Security", "Linux Hardening", "Penetration Testing Basics", "Wireshark", "Cryptography Basics", "Python/Bash"],
        "advanced": ["SOC Monitoring (SIEM/Splunk)", "OWASP Top 10", "Vulnerability Assessment", "Firewall / WAF", "Incident Response"],
        "soft": ["Security Awareness", "Ethical Mindset", "Analytical Investigation"],
        "keywords": ["zero day", "cve vulnerability", "sql injection", "xss", "tls handshake", "intrusion detection", "compliance"]
    },
    "Data Analyst / Business Intelligence": {
        "core": ["SQL Querying", "Python / Pandas", "Power BI / Tableau", "Excel Advanced", "Statistics", "Data Cleaning"],
        "advanced": ["A/B Testing", "Data Warehousing (BigQuery/Snowflake)", "ETL Pipelines", "Business Metrics (CAC, LTV, Churn)"],
        "soft": ["Critical Thinking", "Stakeholder Presentation", "Business Acumen"],
        "keywords": ["dashboard design", "kpi tracking", "cohort analysis", "conversion rate", "data-driven decisions"]
    },
    "DevOps / Cloud Engineer": {
        "core": ["Linux Administration", "Docker", "Git", "Networking Basics", "Bash/Python Scripting"],
        "advanced": ["Kubernetes (K8s)", "Terraform (IaC)", "CI/CD (GitHub Actions/GitLab)", "AWS/GCP/Azure", "Prometheus/Grafana"],
        "soft": ["Incident Response", "Automation Mindset", "Security Awareness"],
        "keywords": ["uptime", "zero downtime deployment", "infrastructure as code", "helm charts", "service mesh", "monitoring"]
    },
    "Product Manager / Business Analyst (BA)": {
        "core": ["Requirement Gathering", "User Stories & Use Cases", "Wireframing (Figma)", "Agile/Scrum", "SQL Basics"],
        "advanced": ["Roadmapping", "Product Analytics", "Market Research", "Feature Prioritization (RICE/MoSCoW)"],
        "soft": ["Leadership", "Stakeholder Negotiation", "Empathy"],
        "keywords": ["product market fit", "user journey mapping", "sprint planning", "acceptance criteria", "retention"]
    },
    "Digital Marketing & Performance Media": {
        "core": ["Google Ads", "Meta Ads (Facebook/Instagram)", "SEO/SEM", "Content Marketing", "Google Analytics (GA4)", "Canva/CapCut"],
        "advanced": ["Conversion Rate Optimization (CRO)", "Marketing Automation (HubSpot/Mailchimp)", "TikTok Ads", "Affiliate Marketing", "ROAS Optimization"],
        "soft": ["Creativity", "Data Analysis", "Consumer Psychology"],
        "keywords": ["cost per click (cpc)", "click through rate (ctr)", "return on ad spend (roas)", "retargeting", "buyer persona", "funnel conversion"]
    },
    "Financial Analyst & Phân tích Tài chính": {
        "core": ["Financial Modeling", "Corporate Finance", "Excel Advanced (VBA/Macros)", "Báo cáo Tài chính (Balance Sheet/P&L/Cash Flow)", "Định giá Doanh nghiệp (DCF)"],
        "advanced": ["Power BI / Python for Finance", "Chứng khoán & Phân tích Ngành", "CFA Level 1 Foundation", "Thẩm định Dự án Đầu tư (NPV/IRR)"],
        "soft": ["Quantitative Thinking", "Attention to Precision", "Risk Management"],
        "keywords": ["ebitda", "wacc", "discounted cash flow", "free cash flow", "ratio analysis", "working capital", "due diligence"]
    },
    "Kế toán & Kiểm toán (Auditing & Accounting)": {
        "core": ["Hạch toán Kế toán", "Luật Thuế GTGT & TNDN", "Phần mềm MISA/FAST", "Chuẩn mực Kế toán (VAS/IFRS)", "Quyết toán Thuế"],
        "advanced": ["Kiểm toán Báo cáo Tài chính", "Kiểm soát Nội bộ", "Excel Chuyên sâu", "Chứng chỉ ACCA/CPA Foundation"],
        "soft": ["Cẩn trọng", "Đạo đức Nghề nghiệp", "Tính Kỷ luật"],
        "keywords": ["bút toán", "sổ cái", "khấu hao", "kiểm kê tài sản", "đối chiếu công nợ", "nguyên tắc dồn tích", "bằng chứng kiểm toán"]
    },
    "HR & Quản trị Nhân sự (Talent Acquisition)": {
        "core": ["Quy trình Tuyển dụng (Sourcing/Screening)", "Phỏng vấn Đánh giá Năng lực", "Luật Lao động Việt Nam", "Đăng tin & Xây dựng Thương hiệu Tuyển dụng"],
        "advanced": ["Đánh giá Hiệu suất (KPIs/OKRs)", "Đào tạo & Phát triển (L&D)", "Hệ thống C&B (Lương & Phúc lợi)", "Văn hóa Doanh nghiệp"],
        "soft": ["Active Listening", "Negotiation", "Conflict Resolution", "Interpersonal Skills"],
        "keywords": ["time to hire", "cost per hire", "headhunting", "onboarding", "retention rate", "mô tả công việc (jd)", "đãi ngộ"]
    },
    "Supply Chain & Quản trị Chuỗi Cung ứng (Logistics)": {
        "core": ["Quản lý Kho bãi (Warehouse)", "Thủ tục Hải quan & Xuất nhập khẩu", "Incoterms 2020", "Vận tải Đa phương thức", "ERP/SAP Basics"],
        "advanced": ["Hoạch định Nhu cầu (Demand Planning)", "Tối ưu Tồn kho (JIT/EOQ)", "Thu mua & Đàm phán Nhà cung cấp (Procurement)", "Freight Forwarding"],
        "soft": ["Problem Solving Under Pressure", "Vendor Relationship Management", "Logical Planning"],
        "keywords": ["bill of lading", "customs clearance", "lead time", "safety stock", "inventory turnover", "fob", "cif", "logistics hub"]
    },
    "UI/UX & Product Designer": {
        "core": ["Figma Advanced", "User Research & Usability Testing", "Wireframing & Prototyping", "Information Architecture", "Design Systems"],
        "advanced": ["Micro-interactions", "Design System Scalability", "Accessibility (WCAG)", "Design Handoff to Developers", "User Persona & Journey Maps"],
        "soft": ["User Empathy", "Visual Aesthetics", "Design Presentation"],
        "keywords": ["auto layout", "component variants", "heuristic evaluation", "a/b testing", "wireframe", "color contrast", "design sprint"]
    },
    "Kỹ sư Tự động hóa & Cơ điện tử (Automation & Robotics)": {
        "core": ["Lập trình PLC (Siemens/Mitsubishi)", "Thiết kế Mạch Điện & Khí nén", "AutoCAD Electrical", "SCADA & HMI", "Cảm biến Công nghiệp"],
        "advanced": ["Cánh tay Robot Công nghiệp", "Thị giác Máy tính (Machine Vision)", "Industrial IoT (MQTT/Modbus)", "Bảo trì Dự đoán"],
        "soft": ["Safety Protocol", "Hands-on Troubleshooting", "Systems Engineering"],
        "keywords": ["ladder logic", "hmi screen", "servo motor", "sensor calibration", "modbus rtu", "safety interlock", "chu trình tự động"]
    },
    "Thương mại Điện tử & Kinh doanh Quốc tế (E-commerce)": {
        "core": ["Vận hành Sàn TMĐT (Shopee/Lazada/TikTok Shop)", "Quản lý Gian hàng & Livestream", "Nghiên cứu Thị trường & Đối thủ", "Xử lý Đơn hàng & CSKH", "Excel Phân tích Bán hàng"],
        "advanced": ["Tối ưu Tỷ lệ Chuyển đổi (CRO)", "Quảng cáo Nội sàn (Shopee Ads/Lazada Ads)", "Xúc tiến Xuất nhập khẩu B2B (Alibaba)", "Chiến lược Định giá Dynamic Pricing"],
        "soft": ["Khả năng thích ứng nhanh", "Kỹ năng đàm phán", "Tư duy dịch vụ khách hàng"],
        "keywords": ["gmv", "aov", "conversion rate", "traffic nội sàn", "flash sale", "livestream", "cross-border", "sku optimization"]
    },
    "Y tế & Dược phẩm (Healthcare & Pharma)": {
        "core": ["Dược lý & Thực hành Tốt (GCP/GLP/GMP)", "Đọc hiểu Tài liệu Lâm sàng", "Quy chế Đăng ký Thuốc & TBYT", "Phân tích Dữ liệu Y sinh", "Kỹ năng Tư vấn Y khoa"],
        "advanced": ["Nghiên cứu Thử nghiệm Lâm sàng (Clinical Trials)", "Dược cảnh giác (Pharmacovigilance)", "Market Access & Đấu thầu Thuốc", "Sinh học Phân tử & Công nghệ Gen"],
        "soft": ["Đạo đức y tế & Tuân thủ", "Tỉ mỉ & Cẩn trọng tuyệt đối", "Giao tiếp chuyên gia y tế"],
        "keywords": ["clinical trial", "regulatory affairs", "gmp compliance", "pharmacokinetics", "dược lực học", "hồ sơ actd", "đấu thầu bảo hiểm y tế"]
    },
    "Quản trị Khách sạn & Du lịch (Hospitality & Tourism)": {
        "core": ["Nghiệp vụ Tiền sảnh & Lễ tân (Front Office)", "Phần mềm Quản lý Khách sạn (Opera/Smile)", "Quy chuẩn Dịch vụ 5 Sao", "Tiếng Anh Du lịch & Giao tiếp Đa văn hóa", "Xử lý Khiếu nại Khách hàng"],
        "advanced": ["Quản trị Doanh thu Khách sạn (Revenue Management)", "Tổ chức Sự kiện & Hội nghị (MICE)", "Quản trị Trải nghiệm Khách hàng cao cấp (CX)", "Thiết kế Tour Trải nghiệm"],
        "soft": ["Thấu cảm & Năng lượng tích cực", "Quản lý khủng hoảng dịch vụ", "Lãnh đạo đội ngũ vận hành"],
        "keywords": ["adr", "revpar", "occupancy rate", "opera pms", "guest journey", "upselling", "butler service", "tiêu chuẩn service 5 sao"]
    },
    "Pháp chế Doanh nghiệp & Luật Kinh tế (Corporate Legal)": {
        "core": ["Rà soát & Soạn thảo Hợp đồng Thương mại", "Luật Doanh nghiệp & Luật Đầu tư", "Thủ tục Cấp phép & Đăng ký Kinh doanh", "Tư vấn Tuân thủ Pháp luật Lao động", "Nghiên cứu Án lệ & Văn bản Pháp quy"],
        "advanced": ["Pháp lý M&A (Mua bán & Sáp nhập)", "Sở hữu Trí tuệ & Chuyển giao Công nghệ", "Giải quyết Tranh chấp Thương mại (VIAC)", "Pháp lý Dữ liệu Cá nhân & Nghị định 13"],
        "soft": ["Tư duy phản biện sắc bén", "Lập luận logic & Chặt chẽ", "Bảo mật thông tin tối mật"],
        "keywords": ["due diligence", "nda", "hợp đồng kinh tế", "m&a", "sở hữu trí tuệ", "tuân thủ pháp chế", "giải quyết tranh chấp", "nghị định 13"]
    },
    "Kỹ sư Xây dựng & Kiến trúc (Civil Engineering & BIM)": {
        "core": ["Mô hình hóa Thông tin Công trình (Revit BIM)", "Bản vẽ Kỹ thuật AutoCAD 2D/3D", "Tính toán Kết cấu (Etabs/SAP2000)", "Dự toán Khối lượng & Chi phí Xây dựng", "Quy chuẩn & Tiêu chuẩn Xây dựng (TCVN)"],
        "advanced": ["Phối hợp BIM & Kiểm tra Xung đột (Navisworks)", "Quản lý Dự án Thi công (Primavera P6/MS Project)", "Kết cấu Thép & Bê tông Dự ứng lực", "Công trình Xanh & Bền vững (LEED/LOTUS)"],
        "soft": ["An toàn lao động trên công trường", "Điều phối nhà thầu phụ", "Làm việc nhóm kỷ luật"],
        "keywords": ["bim revit", "clash detection", "etabs", "khối lượng boq", "biện pháp thi công", "tiến độ gantt", "nghiệm thu kết cấu", "an toàn lao động"]
    },
    "Giáo dục & Công nghệ Giáo dục (EdTech & Training)": {
        "core": ["Thiết kế Bài giảng & Giáo án Số", "Phương pháp Giảng dạy Hiện đại (Active Learning)", "Hệ thống Quản lý Học tập (LMS Moodle/Canvas)", "Kỹ năng Thuyết trình & Sư phạm", "Tạo Nội dung Học liệu Số (Canva/Articulate)"],
        "advanced": ["Thiết kế Trải nghiệm Học tập (Instructional Design)", "Phát triển Khóa học E-learning Tương tác", "Phân tích Hiệu quả Đào tạo (Kirkpatrick)", "Ứng dụng AI trong Cá nhân hóa Học tập"],
        "soft": ["Kiên nhẫn & Truyền cảm hứng", "Lắng nghe & Khích lệ học viên", "Tư duy sáng tạo phương pháp"],
        "keywords": ["instructional design", "lms canvas", "blended learning", "gamification giáo dục", "đánh giá rubrics", "microlearning", "edtech product"]
    }
}

# 1. CV Reviewer & ATS Optimizer
def analyze_cv_content(cv_text: str, target_role: str = "") -> Dict[str, Any]:
    cv_clean = cv_text.strip()
    words = cv_clean.split()
    word_count = len(words)

    # Determine taxonomy
    matched_role = "Backend Developer"
    for role_name in ROLE_SKILL_TAXONOMY.keys():
        if target_role and (target_role.lower() in role_name.lower() or role_name.lower() in target_role.lower()):
            matched_role = role_name
            break
        elif any(k in cv_clean.lower() for k in ROLE_SKILL_TAXONOMY[role_name]["core"][:3]):
            matched_role = role_name
            break

    role_data = ROLE_SKILL_TAXONOMY.get(matched_role, ROLE_SKILL_TAXONOMY["Backend Developer"])

    # ATS Scoring heuristics
    score = 50
    strengths = []
    weaknesses = []
    missing_keywords = []

    # Check length
    if 250 <= word_count <= 900:
        score += 15
        strengths.append(f"Độ dài hồ sơ lý tưởng ({word_count} từ), phù hợp tiêu chuẩn ATS 1 trang.")
    elif word_count < 250:
        score -= 10
        weaknesses.append("Nội dung CV quá ngắn, thiếu chi tiết về các dự án thực tế và kỹ năng.")
    else:
        score += 5
        weaknesses.append("Nội dung CV hơi dài, nên cô đọng lại các gạch đầu dòng để nhà tuyển dụng dễ scan trong 6 giây.")

    # Check for Action Verbs & Metrics (Numbers/%)
    number_matches = re.findall(r'\b\d+[%+kKmMBb]?\b', cv_clean)
    if len(number_matches) >= 3:
        score += 15
        strengths.append(f"Có định lượng kết quả ấn tượng ({len(number_matches)} số liệu / phần trăm thành tích).")
    else:
        weaknesses.append("Thiếu các số liệu định lượng (Metrics). Hãy bổ sung % tối ưu, số người dùng hoặc thời gian hoàn thành.")

    # Check keywords
    cv_lower = cv_clean.lower()
    found_keywords = []
    for kw in role_data["keywords"] + role_data["core"]:
        if kw.lower() in cv_lower:
            found_keywords.append(kw)
        else:
            missing_keywords.append(kw)

    keyword_density_score = min(20, int((len(found_keywords) / max(1, len(role_data["core"]))) * 20))
    score += keyword_density_score

    if found_keywords:
        strengths.append(f"Chứa các từ khóa kỹ thuật chuẩn ATS: {', '.join(found_keywords[:5])}.")

    # Missing critical keywords
    missing_keywords = missing_keywords[:6]

    # Sections check
    has_contact = any(k in cv_lower for k in ["email", "@", "sđt", "phone", "linkedin", "github"])
    has_education = any(k in cv_lower for k in ["học vấn", "education", "đại học", "university", "gpa"])
    has_experience = any(k in cv_lower for k in ["kinh nghiệm", "experience", "dự án", "projects", "hoạt động"])
    has_skills = any(k in cv_lower for k in ["kỹ năng", "skills", "công nghệ", "technologies"])

    sections_ok = sum([has_contact, has_education, has_experience, has_skills])
    if sections_ok == 4:
        score += 10
        strengths.append("Bố cục cấu trúc 4 phần chuẩn mực (Thông tin, Học vấn, Kỹ năng, Dự án).")
    else:
        weaknesses.append("Chưa đầy đủ các đề mục chuẩn: cần bổ sung rõ ràng phần Kỹ năng hoặc Dự án thực tế.")

    ats_score = max(35, min(96, score))

    # Bullet point rewrites into STAR framework
    bullet_rewrites = [
        {
            "original": "Tham gia phát triển trang web bán hàng cho đồ án trường.",
            "improved": "Thiết kế & triển khai RESTful API cho ứng dụng thương mại điện tử bằng FastAPI và React, phục vụ hơn 500 người dùng thử nghiệm với thời gian phản hồi <150ms.",
            "principle": "Cấu trúc STAR: Nêu rõ công nghệ (FastAPI/React), quy mô (500 users) và chỉ số hiệu năng (<150ms)."
        },
        {
            "original": "Làm việc nhóm và hỗ trợ sửa lỗi hệ thống.",
            "improved": "Phối hợp trong nhóm Agile (5 thành viên), tối ưu hóa truy vấn SQL và giải quyết 25+ bug tồn đọng, giúp giảm tỷ lệ lỗi hệ thống xuống 30%.",
            "principle": "Bổ sung hành động chủ động (Agile, tối ưu hóa SQL) kèm kết quả định lượng cụ thể."
        },
        {
            "original": "Có tìm hiểu về trí tuệ nhân tạo và Machine Learning.",
            "improved": "Huấn luyện và đánh giá mô hình phân loại với Scikit-Learn và PyTorch, đạt độ chính xác F1-Score 91% trên tập dữ liệu benchmark 10,000 mẫu.",
            "principle": "Thay thế từ mơ hồ bằng kỹ năng thực chiến và chỉ số đo lường học máy chuẩn."
        }
    ]

    action_recommendations = [
        f"Bổ sung ít nhất 3 từ khóa chuyên ngành còn thiếu: {', '.join(missing_keywords[:3])}.",
        "Chuyển đổi toàn bộ các câu miêu tả trách nhiệm sang công thức: [Động từ hành động mạnh] + [Nhiệm vụ/Công nghệ] + [Kết quả định lượng %].",
        "Đưa link GitHub / Portfolio có README minh họa ảnh chụp màn hình lên đầu CV.",
        "Xuất file dưới định dạng PDF với tên chuẩn: HoTen_ViTriUngTuyen_CV.pdf."
    ]

    return {
        "ats_score": ats_score,
        "target_role": target_role or matched_role,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "missing_keywords": missing_keywords,
        "bullet_rewrites": bullet_rewrites,
        "action_recommendations": action_recommendations
    }

# 2. AI Mock Interview Simulator
INTERVIEW_QUESTION_BANK = {
    "AI / Machine Learning Engineer": [
        {
            "id": 1,
            "type": "Kỹ thuật chuyên sâu",
            "question": "Bạn hãy giải thích sự khác biệt giữa Overfitting và Underfitting trong Machine Learning. Trong dự án thực tế, bạn áp dụng những kỹ thuật nào để ngăn chặn hiện tượng Overfitting?",
            "hints": ["Đề cập đến Train/Validation error", "Các kỹ thuật: Regularization (L1/L2), Dropout, Data Augmentation, Early Stopping, Cross-Validation."],
            "ideal_keywords": ["regularization", "dropout", "validation", "early stopping", "cross validation", "generalization"]
        },
        {
            "id": 2,
            "type": "Tình huống & Hệ thống",
            "question": "Giả sử bạn phải xây dựng một mô hình gợi ý việc làm cho sinh viên với tập dữ liệu hàng nghìn việc làm và hồ sơ. Bạn sẽ thiết kế pipeline xử lý dữ liệu và thuật toán matching như thế nào?",
            "hints": ["Trích xuất feature văn bản (TF-IDF hoặc Embedding)", "Tính toán tương đồng (Cosine Similarity)", "Kết hợp trọng số kỹ năng cứng và nguyện vọng."],
            "ideal_keywords": ["embedding", "tfidf", "cosine similarity", "pipeline", "preprocessing", "latency"]
        },
        {
            "id": 3,
            "type": "Hành vi (STAR Behavioral)",
            "question": "Hãy kể lại một lần mô hình AI của bạn cho kết quả không như kỳ vọng hoặc gặp sự cố bất ngờ. Bạn đã tìm nguyên nhân và khắc phục nó ra sao?",
            "hints": ["S - Tình huống gặp lỗi", "T - Mục tiêu cần đạt", "A - Các bước debug dữ liệu/mô hình", "R - Kết quả sau khi cải tiến."],
            "ideal_keywords": ["tình huống", "nguyên nhân", "debug", "dữ liệu", "kết quả", "cải thiện"]
        }
    ],
    "Backend Developer": [
        {
            "id": 1,
            "type": "Kỹ thuật chuyên sâu",
            "question": "Bạn hãy giải thích nguyên lý hoạt động của Cơ sở dữ liệu quan hệ khi tối ưu hóa truy vấn: Index (Chỉ mục) giúp tăng tốc độ tìm kiếm như thế nào và khi nào thì việc đánh Index quá nhiều lại gây hại?",
            "hints": ["Cấu trúc B-Tree", "Tăng tốc SELECT nhưng làm chậm INSERT/UPDATE/DELETE", "Dung lượng bộ nhớ."],
            "ideal_keywords": ["btree", "index", "select", "insert", "update", "chỉ mục", "tối ưu"]
        },
        {
            "id": 2,
            "type": "Tình huống & Thiết kế",
            "question": "Hệ thống API đặt chỗ thực tập của bạn bị nghẽn mạng do 10,000 sinh viên cùng truy cập nộp hồ sơ tại thời điểm mở cổng tuyển dụng. Bạn sẽ xử lý vấn đề quá tải (High Concurrency) như thế nào?",
            "hints": ["Caching với Redis", "Message Queue (Kafka, RabbitMQ, Celery)", "Rate limiting", "Database connection pooling."],
            "ideal_keywords": ["redis", "cache", "queue", "message queue", "rate limit", "asynchronous", "pool"]
        },
        {
            "id": 3,
            "type": "Hành vi (STAR Behavioral)",
            "question": "Hãy kể về một lần bạn và thành viên trong nhóm bất đồng quan điểm về giải pháp kỹ thuật hoặc kiến trúc mã nguồn. Bạn đã giải quyết mâu thuẫn đó như thế nào?",
            "hints": ["Lắng nghe tích cực", "Dựa trên số liệu và benchmark thay vì cảm tính", "Tìm giải pháp tối ưu cho toàn đội."],
            "ideal_keywords": ["lắng nghe", "trao đổi", "benchmark", "thống nhất", "giải pháp", "kết quả"]
        }
    ],
    "Frontend Developer": [
        {
            "id": 1,
            "type": "Kỹ thuật chuyên sâu",
            "question": "Bạn hãy giải thích cơ chế Virtual DOM trong React và cách React tối ưu hóa việc render lại (re-render) linh kiện khi state thay đổi. Khi nào bạn sử dụng useMemo và useCallback?",
            "hints": ["Reconciliation algorithm", "Diffing algorithm", "Tránh tính toán lại tốn kém và ghi nhớ tham chiếu hàm."],
            "ideal_keywords": ["virtual dom", "diffing", "re-render", "usememo", "usecallback", "hiệu năng"]
        },
        {
            "id": 2,
            "type": "Tình huống & Thiết kế",
            "question": "Trang web của bạn bị người dùng phản hồi là tải chậm và giật lag trên thiết bị di động. Bạn sẽ sử dụng các công cụ nào để đo lường và những giải pháp nào để tối ưu tốc độ tải trang (Core Web Vitals)?",
            "hints": ["Lighthouse, Chrome DevTools", "Code splitting (React.lazy)", "Tối ưu hóa ảnh (WebP, lazy load)", "CDN, giảm bundle size."],
            "ideal_keywords": ["lighthouse", "lazy loading", "code splitting", "bundle", "webp", "fcp", "lcp"]
        },
        {
            "id": 3,
            "type": "Hành vi (STAR Behavioral)",
            "question": "Khi nhận được bản thiết kế UI rất phức tạp từ Designer với thời gian bàn giao gấp gáp, bạn sẽ lập kế hoạch thực hiện như thế nào để vừa kịp tiến độ vừa đảm bảo trải nghiệm người dùng?",
            "hints": ["Chia nhỏ component", "Trao đổi với Designer về các tương tác khả thi", "Ưu tiên MVP (tính năng cốt lõi trước)."],
            "ideal_keywords": ["chia nhỏ", "ưu tiên", "mvp", "trao đổi", "tiến độ", "kết quả"]
        }
    ],
    "Digital Marketing & Performance Media": [
        {
            "id": 1,
            "type": "Chuyên môn & Đo lường",
            "question": "Trong chiến dịch quảng cáo kỹ thuật số, bạn đo lường và tối ưu hóa chỉ số ROAS (Return on Ad Spend) và CAC (Customer Acquisition Cost) như thế nào khi chi phí chạy Ads có xu hướng tăng cao?",
            "hints": ["A/B Testing nội dung/hình ảnh", "Tối ưu phễu chuyển đổi (CRO)", "Retargeting tệp khách hàng tiềm năng", "LTV so với CAC."],
            "ideal_keywords": ["roas", "cac", "ctr", "cvr", "a/b test", "retargeting", "tối ưu phễu", "chuyển đổi"]
        },
        {
            "id": 2,
            "type": "Tình huống & Chiến lược",
            "question": "Nếu công ty chuẩn bị ra mắt một sản phẩm mới hướng đến nhóm khách hàng sinh viên và Gen Z với ngân sách hạn chế, bạn sẽ xây dựng kế hoạch phân phối nội dung đa kênh (Omnichannel) như thế nào?",
            "hints": ["TikTok / Reels viral content", "KOC / Micro-influencers", "User Generated Content (UGC)", "SEO bài viết ngách."],
            "ideal_keywords": ["tiktok", "gen z", "koc", "ugc", "nội dung", "viral", "ngân sách", "chuyển đổi"]
        },
        {
            "id": 3,
            "type": "Hành vi (STAR Behavioral)",
            "question": "Hãy kể lại một chiến dịch truyền thông hoặc bài viết bạn từng thực hiện có lượt tương tác kém hơn kỳ vọng. Bạn đã phân tích nguyên nhân và xoay chuyển tình thế ra sao?",
            "hints": ["S - Mục tiêu chiến dịch", "T - Kết quả ban đầu", "A - Phân tích dữ liệu & điều chỉnh thông điệp", "R - Tăng trưởng sau tối ưu."],
            "ideal_keywords": ["phân tích", "chỉ số", "thông điệp", "điều chỉnh", "kết quả", "bài học"]
        }
    ],
    "Financial Analyst & Phân tích Tài chính": [
        {
            "id": 1,
            "type": "Chuyên môn Định giá & Phân tích",
            "question": "Bạn hãy giải thích mối quan hệ giữa ba báo cáo tài chính chính (Bảng cân đối kế toán, Báo cáo kết quả kinh doanh và Báo cáo lưu chuyển tiền tệ). Nếu chi phí khấu hao tăng 10 triệu đồng, ba báo cáo này sẽ thay đổi như thế nào?",
            "hints": ["P&L: Lợi nhuận trước thuế giảm, thuế thu nhập giảm, Lợi nhuận ròng giảm", "Cash Flow: Khấu hao cộng ngược lại vào dòng tiền từ HĐKD", "Balance Sheet: Tiền mặt tăng, Giá trị TSCĐ giảm."],
            "ideal_keywords": ["bảng cân đối", "lưu chuyển tiền tệ", "khấu hao", "thuế", "lợi nhuận ròng", "dòng tiền", "tài sản"]
        },
        {
            "id": 2,
            "type": "Tình huống Thẩm định Dự án",
            "question": "Khi ban giám đốc cân nhắc giữa hai dự án đầu tư mở rộng thị trường, bạn sẽ sử dụng các phương pháp định giá nào (NPV, IRR, Payback Period, DCF) để tư vấn ra quyết định?",
            "hints": ["NPV là tiêu chí ưu tiên hàng đầu", "IRR so sánh với WACC / Hurdle Rate", "Chiết khấu dòng tiền tự do FCF."],
            "ideal_keywords": ["npv", "irr", "dcf", "wacc", "chiết khấu", "dòng tiền", "rủi ro", "hoàn vốn"]
        },
        {
            "id": 3,
            "type": "Hành vi (STAR Behavioral)",
            "question": "Hãy kể về một lần bạn phát hiện ra một số liệu bất thường hoặc rủi ro tiềm ẩn trong báo cáo dữ liệu của dự án. Bạn đã báo cáo và đề xuất giải pháp ra sao?",
            "hints": ["S - Dữ liệu bất thường", "T - Xác minh nguồn gốc", "A - Trao đổi cùng phòng ban phụ trách", "R - Ngăn chặn thiệt hại."],
            "ideal_keywords": ["số liệu", "bất thường", "kiểm tra", "cảnh báo", "giải pháp", "chính xác"]
        }
    ],
    "Supply Chain & Quản trị Chuỗi Cung ứng (Logistics)": [
        {
            "id": 1,
            "type": "Nghiệp vụ Logistics & Kho bãi",
            "question": "Bạn hãy phân biệt điều kiện Incoterms 2020 giữa FOB và CIF. Trong trường hợp giá cước vận tải biển quốc tế biến động mạnh, doanh nghiệp xuất khẩu nên lựa chọn điều kiện nào để giảm thiểu rủi ro?",
            "hints": ["FOB: Người bán giao hàng qua lan can tàu tại cảng bốc, người mua chịu cước tàu và bảo hiểm", "CIF: Người bán chịu cước và bảo hiểm", "Phân tích biên độ rủi ro chi phí vận chuyển."],
            "ideal_keywords": ["fob", "cif", "incoterms", "cước biển", "bảo hiểm", "rủi ro", "cảng", "hải quan"]
        },
        {
            "id": 2,
            "type": "Tình huống Chuỗi Cung ứng",
            "question": "Giả sử chuỗi cung ứng của công ty bị đứt gãy do nhà cung cấp nguyên vật liệu chính giao trễ 2 tuần, bạn sẽ triển khai phương án ứng phó (Contingency Plan) như thế nào để nhà máy không phải dừng sản xuất?",
            "hints": ["Safety stock (Tồn kho an toàn)", "Nhà cung cấp phụ trợ (Backup suppliers)", "Điều chỉnh kế hoạch sản xuất linh hoạt."],
            "ideal_keywords": ["tồn kho an toàn", "safety stock", "nhà cung cấp", "dự phòng", "kế hoạch", "linh hoạt"]
        },
        {
            "id": 3,
            "type": "Hành vi (STAR Behavioral)",
            "question": "Hãy chia sẻ một kỷ niệm bạn từng phối hợp cùng đơn vị vận chuyển hoặc đối tác kho bãi giải quyết sự cố đơn hàng gấp hoặc thủ tục thông quan bị ách tắc.",
            "hints": ["Giao tiếp chủ động", "Tìm hiểu quy định hải quan", "Đưa hàng đến đích đúng cam kết."],
            "ideal_keywords": ["thông quan", "xử lý", "đối tác", "kịp thời", "kết quả", "cam kết"]
        }
    ],
    "HR & Quản trị Nhân sự (Talent Acquisition)": [
        {
            "id": 1,
            "type": "Nghiệp vụ Tuyển dụng & Đánh giá",
            "question": "Bạn sử dụng phương pháp phỏng vấn theo mô hình STAR và thang đánh giá năng lực (Competency Framework) như thế nào để phát hiện ứng viên có phù hợp với văn hóa tổ chức?",
            "hints": ["Đặt câu hỏi đào sâu hành vi quá khứ", "Thước đo hành vi cụ thể", "Đánh giá mức độ trung thực và tính gắn kết."],
            "ideal_keywords": ["star", "năng lực", "văn hóa", "hành vi", "đánh giá", "tuyển dụng", "khớp nối"]
        },
        {
            "id": 2,
            "type": "Tình huống Nhân sự",
            "question": "Khi thị trường khan hiếm nhân sự chất lượng cao và các ứng viên nhận được nhiều lời mời làm việc cùng lúc, bạn sẽ làm gì để nâng cao tỷ lệ ứng viên đồng ý nhận Offer (Offer Acceptance Rate)?",
            "hints": ["Quy trình tuyển dụng nhanh gọn (Candidate Experience)", "Thương hiệu nhà tuyển dụng (EVP)", "Lắng nghe kỳ vọng cá nhân của ứng viên."],
            "ideal_keywords": ["offer", "trải nghiệm ứng viên", "thương hiệu", "đãi ngộ", "giao tiếp", "tỷ lệ nhận việc"]
        },
        {
            "id": 3,
            "type": "Hành vi (STAR Behavioral)",
            "question": "Hãy kể lại một tình huống bạn phải đóng vai trò trung gian xử lý mâu thuẫn hoặc thấu cảm lắng nghe tâm tư của một thành viên trong đội ngũ.",
            "hints": ["Lắng nghe không phán xét", "Đặt lợi ích chung lên trên", "Tìm giải pháp hài hòa đôi bên."],
            "ideal_keywords": ["lắng nghe", "thấu hiểu", "mâu thuẫn", "giải pháp", "gắn kết", "kết quả"]
        }
    ],
    "UI/UX & Product Designer": [
        {
            "id": 1,
            "type": "Chuyên môn Thiết kế & Quy trình",
            "question": "Bạn hãy mô tả quy trình thực hiện User Research (Nghiên cứu người dùng) trước khi bắt tay vào thiết kế wireframe cho một ứng dụng di động mới. Làm thế nào để cân bằng giữa thẩm mỹ thị giác và tính khả dụng (Usability)?",
            "hints": ["User Interview, khảo sát, Empathy Map", "User Flow và Wireframe sơ cấp", "Usability Testing (Đo lường thời gian hoàn thành tác vụ)", "Tuân thủ Design System và chuẩn WCAG."],
            "ideal_keywords": ["user research", "usability", "wireframe", "prototype", "figma", "testing", "khả dụng", "trải nghiệm"]
        },
        {
            "id": 2,
            "type": "Tình huống & Phối hợp Kỹ thuật",
            "question": "Khi bản thiết kế của bạn bị đội ngũ Kỹ sư Lập trình phản hồi là 'quá phức tạp để triển khai trong sprint 2 tuần', bạn sẽ trao đổi và điều chỉnh thiết kế ra sao mà vẫn bảo toàn trải nghiệm người dùng cốt lõi?",
            "hints": ["Tìm hiểu rào cản kỹ thuật", "Phân tách thành các giai đoạn MVP", "Tái sử dụng các component có sẵn trong Design System."],
            "ideal_keywords": ["trao đổi", "developer", "mvp", "component", "tinh gọn", "khả thi", "tiến độ"]
        },
        {
            "id": 3,
            "type": "Hành vi (STAR Behavioral)",
            "question": "Hãy kể về một lần thiết kế của bạn nhận phải nhiều phản hồi trái chiều (Negative Feedback) từ người dùng thử nghiệm. Bạn đã đón nhận và cải tiến nó như thế nào?",
            "hints": ["Không tự ái nghề nghiệp", "Dựa trên dữ liệu hành vi thực tế", "Lặp lại thiết kế (Iterative Design) để cải thiện chỉ số."],
            "ideal_keywords": ["phản hồi", "dữ liệu", "cải tiến", "kiểm thử", "kết quả", "trải nghiệm"]
        }
    ]
}

def get_mock_questions(role_title: str) -> List[Dict[str, Any]]:
    for key, questions in INTERVIEW_QUESTION_BANK.items():
        if key.lower() in role_title.lower() or role_title.lower() in key.lower():
            return questions
    # Default fallback questions
    return INTERVIEW_QUESTION_BANK["Backend Developer"]

def evaluate_interview_answer(role_title: str, question: Dict[str, Any], answer_text: str) -> Dict[str, Any]:
    ans = answer_text.strip()
    word_count = len(ans.split())

    if word_count < 10:
        return {
            "score": 3.5,
            "criteria_scores": {"clarity": 4.0, "technical_depth": 3.0, "star_method": 3.0, "confidence": 4.0},
            "strengths": ["Bạn đã cố gắng bắt đầu câu trả lời."],
            "improvements": ["Câu trả lời quá ngắn. Hãy phân tích chi tiết hơn các khái niệm kỹ thuật và chia sẻ ví dụ thực tế."],
            "ideal_answer_model": f"Một câu trả lời tốt cho câu hỏi này cần tập trung vào: {', '.join(question.get('hints', []))}."
        }

    # Keyword analysis
    ideal_keywords = question.get("ideal_keywords", [])
    found_kw = [kw for kw in ideal_keywords if kw.lower() in ans.lower()]
    kw_ratio = len(found_kw) / max(1, len(ideal_keywords))

    base_score = 6.0 + (kw_ratio * 3.0)
    if word_count > 60:
        base_score += 0.8
    if any(m in ans.lower() for m in ["ví dụ", "trong dự án", "cụ thể là", "kết quả", "sau đó"]):
        base_score += 0.5

    final_score = min(9.8, round(base_score, 1))

    clarity = min(10.0, round(final_score + 0.3, 1))
    tech_depth = min(10.0, round(5.0 + kw_ratio * 4.5, 1))
    star_method = min(10.0, round(6.5 + (0.5 if word_count > 50 else 0), 1))
    confidence = min(10.0, round(final_score, 1))

    strengths = []
    if found_kw:
        strengths.append(f"Nhắc đúng các khái niệm trọng tâm: {', '.join(found_kw)}.")
    if word_count >= 50:
        strengths.append("Độ dài câu trả lời đầy đặn, diễn đạt mạch lạc và có dẫn chứng.")
    else:
        strengths.append("Đi thẳng vào trọng tâm câu hỏi, không lan man.")

    improvements = []
    missing_kw = [kw for kw in ideal_keywords if kw not in found_kw]
    if missing_kw:
        improvements.append(f"Nên đề cập thêm thuật ngữ kỹ thuật cốt lõi: {', '.join(missing_kw[:3])}.")
    if "ví dụ" not in ans.lower():
        improvements.append("Nên gắn câu trả lời với một dự án hoặc trải nghiệm thực tế bạn đã từng làm ở trường.")
    improvements.append("Áp dụng cấu trúc STAR (Tình huống -> Nhiệm vụ -> Hành động -> Kết quả đạt được) để tăng tính thuyết phục.")

    ideal_model = f"Ví dụ câu trả lời xuất sắc (Điểm 10/10):\n'Khi gặp vấn đề này, trước hết em sẽ {question.get('hints', ['phân tích nguyên nhân'])[0].lower()}. Cụ thể trong dự án của em, em đã áp dụng {', '.join(ideal_keywords[:3])}. Nhờ đó, hệ thống hoạt động ổn định và đạt kết quả vượt bậc.'"

    return {
        "score": final_score,
        "criteria_scores": {
            "clarity": clarity,
            "technical_depth": tech_depth,
            "star_method": star_method,
            "confidence": confidence
        },
        "strengths": strengths,
        "improvements": improvements,
        "ideal_answer_model": ideal_model
    }

# 3. Skill Gap Analysis & Learning Roadmap
def generate_skill_roadmap(target_role: str, current_skills: List[str]) -> Dict[str, Any]:
    matched_role = "Backend Developer"
    for role_name in ROLE_SKILL_TAXONOMY.keys():
        if target_role.lower() in role_name.lower() or role_name.lower() in target_role.lower():
            matched_role = role_name
            break

    role_data = ROLE_SKILL_TAXONOMY[matched_role]
    all_needed = role_data["core"] + role_data["advanced"]
    
    current_lower = {s.lower().strip() for s in current_skills}
    missing = [s for s in all_needed if not any(c in s.lower() or s.lower() in c for c in current_lower)]
    
    readiness = int(((len(all_needed) - len(missing)) / len(all_needed)) * 100)
    readiness = max(25, min(95, readiness))

    milestones = [
        {
            "phase": "Giai đoạn 1: Nền tảng chuyên môn vững chắc (Tuần 1 - Tuần 4)",
            "goal": "Làm chủ kiến trúc và cú pháp cốt lõi của công nghệ mục tiêu",
            "skills": [s for s in role_data["core"] if s in missing][:3] or role_data["core"][:3],
            "actions": [
                "Nắm vững các nguyên lý lập trình chuẩn mực và cấu trúc dữ liệu cơ bản.",
                "Thực hành viết các module chức năng độc lập có Unit Test độ bao phủ >80%.",
                "Hoàn thành các bài tập thuật toán căn bản trên LeetCode / HackerRank."
            ],
            "resources": "Tài liệu chính thức (Official Docs) & Khóa học Coursera / Udemy uy tín."
        },
        {
            "phase": "Giai đoạn 2: Xây dựng Dự án thực chiến Capstone (Tuần 5 - Tuần 8)",
            "goal": "Phát triển một sản phẩm hoàn chỉnh end-to-end giải quyết bài toán thực tế",
            "skills": [s for s in role_data["advanced"] if s in missing][:2] or role_data["advanced"][:2],
            "actions": [
                f"Xây dựng dự án ứng dụng thực tiễn giải quyết bài toán ngành {matched_role}.",
                "Tích hợp Database, caching, xác thực JWT và đóng gói container với Docker.",
                "Viết README chi tiết, mô tả kiến trúc (Architecture Diagram) và hướng dẫn chạy."
            ],
            "resources": "GitHub Open Source repos, Real-world Project boilerplate, Docker docs."
        },
        {
            "phase": "Giai đoạn 3: Tối ưu hiệu năng & Triển khai thực tế (Tuần 9 - Tuần 11)",
            "goal": "Triển khai Cloud, CI/CD và đạt chứng chỉ ngành nghề có giá trị",
            "skills": ["CI/CD Pipeline", "Cloud Deployment (AWS/GCP)", "Performance Profiling"],
            "actions": [
                "Cấu hình GitHub Actions tự động kiểm thử và deploy lên Cloud server.",
                "Đo lường độ trễ (latency), tối ưu hóa tốc độ tải và xử lý ngoại lệ an toàn.",
                "Ôn tập và thi chứng chỉ liên quan (AWS Cloud Practitioner / Google Cloud / Coursera Spec)."
            ],
            "resources": "AWS Free Tier / Google Cloud Skills Boost, GitHub Actions marketplace."
        },
        {
            "phase": "Giai đoạn 4: Hoàn thiện Portfolio & Chinh phục Phỏng vấn (Tuần 12)",
            "goal": "Sẵn sàng 100% ứng tuyển và gây ấn tượng mạnh với nhà tuyển dụng",
            "skills": ["ATS CV Optimization", "Mock Interview Prep", "Professional Networking"],
            "actions": [
                "Đưa hồ sơ lên CareerBridge AI để chấm điểm ATS đạt trên 85 điểm.",
                "Thực hành ít nhất 5 phiên phỏng vấn thử (AI Mock Interview) với câu hỏi tình huống.",
                "Kết nối với cựu sinh viên và các nhà tuyển dụng trên mạng lưới hướng nghiệp trường."
            ],
            "resources": "CareerBridge AI Mock Simulator & Trung tâm hỗ trợ việc làm sinh viên."
        }
    ]

    return {
        "target_role": target_role,
        "current_skills": current_skills,
        "missing_skills": missing,
        "readiness_percentage": readiness,
        "milestones": milestones
    }

# 4. AI Career Advisor Chatbot Engine
def generate_career_chat_response(
    message: str,
    session_id: str,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    from ..database import db_session
    from datetime import datetime
    import uuid

    msg_clean = message.strip()
    msg_lower = msg_clean.lower()
    now_iso = datetime.now().isoformat()
    context = context or {}

    # Extract user profile context if available
    student_name = context.get("full_name") or "bạn"
    student_major = context.get("major") or ""
    student_skills = context.get("skills") or []
    student_roles = context.get("dream_roles") or []

    intent = "general_faq"
    reply = ""
    suggestions = []
    suggested_jobs = []

    # Intent Detection
    is_job_search = any(k in msg_lower for k in ["tìm việc", "việc làm", "tuyển dụng", "thực tập", "fresher", "intern", "công việc", "apply", "ứng tuyển", "vị trí"])
    is_salary = any(k in msg_lower for k in ["lương", "thu nhập", "mức lương", "bao nhiêu tiền", "đãi ngộ", "deal lương", "salary"])
    is_cv = any(k in msg_lower for k in ["cv", "hồ sơ", "ats", "viết cv", "portfolio", "sửa cv", "resume"])
    is_interview = any(k in msg_lower for k in ["phỏng vấn", "interview", "trả lời câu hỏi", "điểm yếu", "giới thiệu bản thân", "nhà tuyển dụng hỏi"])
    is_roadmap = any(k in msg_lower for k in ["lộ trình", "roadmap", "học gì", "bắt đầu từ đâu", "tự học", "khóa học", "kỹ năng cần có"])
    is_guidance = any(k in msg_lower for k in ["định hướng", "chọn ngành", "chọn nghề", "phù hợp", "không biết làm gì", "chuyển ngành", "tương lai", "nghề gì hot"])

    # Attempt LLM call if GEMINI_API_KEY is configured
    llm_succeeded = False
    if GEMINI_API_KEY:
        try:
            system_prompt = (
                "Bạn là CareerBridge AI - Chuyên gia Cố vấn Hướng nghiệp và Tuyển dụng hàng đầu Việt Nam. "
                "Nhiệm vụ của bạn là hỗ trợ sinh viên định hướng nghề nghiệp, tìm việc làm, tối ưu CV, luyện phỏng vấn, "
                "và xây dựng lộ trình nâng cao kỹ năng cho 16+ ngành nghề tại Việt Nam. "
                "Phong cách: Tận tâm, chuyên nghiệp, khích lệ, dùng định dạng Markdown rõ ràng, gạch đầu dòng và số liệu định lượng."
            )
            context_prompt = ""
            if student_major or student_skills:
                context_prompt = f"Thông tin sinh viên: Tên {student_name}, Ngành {student_major}, Kỹ năng: {', '.join(student_skills[:5])}, Mục tiêu: {', '.join(student_roles[:3])}. "

            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": f"{system_prompt}\n{context_prompt}\nCâu hỏi của sinh viên: {msg_clean}"}]}
                ],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1000}
            }
            with httpx.Client(timeout=10.0) as client:
                res = client.post(gemini_url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        reply = candidates[0]["content"]["parts"][0]["text"]
                        llm_succeeded = True
        except Exception:
            llm_succeeded = False

    # High-Fidelity Domain Knowledge Engine (Active when no LLM key or offline fallback)
    if not llm_succeeded:
        if is_job_search:
            intent = "job_search"
            # Search database for matching jobs
            with db_session() as conn:
                cursor = conn.cursor()
                # Find matching jobs by searching title, description, or industry
                search_terms = [t for t in ["AI", "Backend", "Frontend", "Data", "Marketing", "Tài chính", "Logistics", "HR", "Design", "Tự động hóa", "Phần mềm", "Thương mại", "Dược", "Khách sạn", "Luật", "BIM", "Giáo dục"] if t.lower() in msg_lower]
                
                query = "SELECT * FROM job_postings WHERE is_active = 1"
                params = []
                if search_terms:
                    query += " AND (" + " OR ".join(["title LIKE ? OR industry LIKE ? OR required_skills LIKE ?" for _ in search_terms]) + ")"
                    for term in search_terms:
                        params.extend([f"%{term}%", f"%{term}%", f"%{term}%"])
                query += " ORDER BY created_at DESC LIMIT 4"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                if not rows:
                    cursor.execute("SELECT * FROM job_postings WHERE is_active = 1 ORDER BY created_at DESC LIMIT 4")
                    rows = cursor.fetchall()
                
                for r in rows:
                    skills_list = []
                    try:
                        skills_list = json.loads(r["required_skills"])
                    except Exception:
                        skills_list = []
                    suggested_jobs.append({
                        "id": r["id"],
                        "title": r["title"],
                        "company_name": r["company_name"],
                        "location": r["location"],
                        "salary_range": r["salary_range"],
                        "job_type": r["job_type"],
                        "industry": r["industry"],
                        "required_skills": skills_list[:4]
                    })

            reply = f"Chào **{student_name}**, tôi đã quét qua hệ thống và tìm thấy các cơ hội thực tập & việc làm nổi bật phù hợp với bạn:\n\n"
            for idx, j in enumerate(suggested_jobs, 1):
                reply += f"### {idx}. {j['title']} — **{j['company_name']}**\n"
                reply += f"- 📍 **Địa điểm**: {j['location']} | 🏷️ **Hình thức**: {j['job_type']}\n"
                reply += f"- 💰 **Mức lương**: `{j['salary_range']}`\n"
                reply += f"- 🛠️ **Kỹ năng chính**: {', '.join(j['required_skills'])}\n"
                reply += f"- 🔗 *Bạn có thể xem chi tiết và nộp hồ sơ trực tiếp trong tab **Việc làm**.*\n\n"

            reply += "> 💡 **Lời khuyên AI**: Hãy dùng tính năng **Tối ưu CV (ATS)** trước khi nộp để tăng tỷ lệ được gọi phỏng vấn lên 90%!"
            suggestions = [
                "Cách viết CV chuẩn ATS cho vị trí này",
                "Mức lương trung bình của vị trí này là bao nhiêu?",
                "Phỏng vấn thử cho vị trí này"
            ]

        elif is_salary:
            intent = "salary_inquiry"
            reply = (
                f"Chào **{student_name}**, dưới đây là bảng thống kê **Mức lương Thị trường 2026** cho Thực tập sinh (Intern) và Mới tốt nghiệp (Fresher) tại Việt Nam:\n\n"
                "| Nhóm ngành nghề | Mức lương Thực tập (Intern) | Mức lương Fresher (0-1 năm KN) |\n"
                "| :--- | :--- | :--- |\n"
                "| 🤖 **AI & Khoa học Dữ liệu** | 7.0 - 12.0 triệu VNĐ | 14.0 - 25.0 triệu VNĐ |\n"
                "| 💻 **CNTT & Kỹ sư Phần mềm** | 6.0 - 10.0 triệu VNĐ | 12.0 - 20.0 triệu VNĐ |\n"
                "| 🛡️ **An toàn Thông tin (Cyber)** | 6.5 - 11.0 triệu VNĐ | 13.0 - 22.0 triệu VNĐ |\n"
                "| 📊 **Phân tích Tài chính & Đầu tư** | 6.0 - 10.0 triệu VNĐ | 12.0 - 22.0 triệu VNĐ |\n"
                "| 📢 **Digital Marketing & Ads** | 5.0 - 8.5 triệu VNĐ | 9.0 - 16.0 triệu VNĐ |\n"
                "| 🚚 **Logistics & Chuỗi Cung ứng** | 5.5 - 9.0 triệu VNĐ | 9.5 - 16.5 triệu VNĐ |\n"
                "| 🎨 **UI/UX & Product Design** | 6.0 - 10.0 triệu VNĐ | 11.0 - 18.0 triệu VNĐ |\n"
                "| ⚙️ **Kỹ thuật & Tự động hóa** | 6.5 - 10.5 triệu VNĐ | 11.0 - 19.0 triệu VNĐ |\n"
                "| 🛒 **E-commerce Operations** | 5.0 - 8.5 triệu VNĐ | 9.0 - 15.0 triệu VNĐ |\n"
                "| 💊 **Y tế & Dược lâm sàng** | 5.5 - 9.0 triệu VNĐ | 10.0 - 17.0 triệu VNĐ |\n"
                "| ⚖️ **Pháp chế Doanh nghiệp** | 5.0 - 8.0 triệu VNĐ | 9.0 - 16.0 triệu VNĐ |\n\n"
                "> 💡 **Bí quyết deal lương**: Đừng chỉ nêu con số mong muốn, hãy chứng minh bằng **dự án thực chiến**, chứng chỉ uy tín và kết quả bài test kỹ thuật!"
            )
            suggestions = [
                "Cách trả lời khi nhà tuyển dụng hỏi mức lương mong muốn",
                "Tìm việc thực tập lương từ 8 triệu",
                "Lộ trình tăng lương sau 1 năm đi làm"
            ]

        elif is_cv:
            intent = "cv_advice"
            reply = (
                f"Chào **{student_name}**, để CV của bạn vượt qua hệ thống lọc tự động (ATS) và chinh phục nhà tuyển dụng trong 6 giây đầu tiên, hãy áp dụng bộ nguyên tắc sau:\n\n"
                "### 1. Cấu trúc chuẩn mực 1 trang (1-Page ATS Standard)\n"
                "- **Thông tin cá nhân**: Họ tên, Email chuyên nghiệp, SĐT, Link LinkedIn / GitHub / Portfolio.\n"
                "- **Mục tiêu nghề nghiệp**: Ngắn gọn 2-3 câu, nêu rõ giá trị bạn mang lại cho doanh nghiệp.\n"
                "- **Kỹ năng chuyên môn**: Chia nhóm Kỹ năng Cốt lõi (Core), Kỹ năng Nâng cao (Tools/Frameworks) và Ngoại ngữ.\n"
                "- **Dự án thực tế (Quan trọng nhất)**: Trình bày từ 2-3 dự án tiêu biểu nhất.\n"
                "- **Học vấn & Chứng chỉ**: Tên trường, chuyên ngành, GPA (nếu >= 3.0), các chứng chỉ quốc tế.\n\n"
                "### 2. Công thức viết thành tích STAR\n"
                "Thay vì viết: *'Làm việc nhóm xây dựng website bán hàng'*, hãy viết:\n"
                "> *'Thiết kế RESTful API bằng FastAPI & PostgreSQL cho sàn TMĐT với 500 users thử nghiệm, giảm thời gian phản hồi còn 120ms.'*\n\n"
                "### 3. Đặt tên file chuẩn gửi nhà tuyển dụng\n"
                "- Chuẩn: `CV_[Vị_Trí]_[Họ_Và_Tên].pdf` (Ví dụ: `CV_Backend_Intern_NguyenVanA.pdf`).\n\n"
                "👉 Bạn có thể dán nội dung CV vào tính năng **Tối ưu CV** trên thanh Menu để AI chấm điểm và sửa từng gạch đầu dòng nhé!"
            )
            suggestions = [
                "Ví dụ câu viết theo công thức STAR",
                "CV sinh viên chưa có kinh nghiệm nên viết gì?",
                "Chuyển đến công cụ Tối ưu CV"
            ]

        elif is_interview:
            intent = "interview_prep"
            reply = (
                f"Chào **{student_name}**, phỏng vấn là cơ hội để bạn chứng minh sự phù hợp về văn hóa và năng lực giải quyết vấn đề. Dưới đây là chiến lược cho các câu hỏi kinh điển:\n\n"
                "### 1. 'Hãy giới thiệu bản thân trong 2 phút?'\n"
                "- **Công thức Hiện tại - Quá khứ - Tương lai**: Nêu bạn là ai (chuyên ngành, thế mạnh hiện tại) ➔ 1 thành tựu nổi bật bạn tự hào nhất ➔ Lý do vì sao bạn có mặt ở buổi phỏng vấn hôm nay.\n\n"
                "### 2. 'Điểm yếu lớn nhất của bạn là gì?'\n"
                "- **Cách trả lời điểm 10**: Chọn một điểm yếu THẬT nhưng không phải kỹ năng cốt lõi bắt buộc, và nêu ngay **biện pháp cụ thể bạn đang khắc phục**.\n"
                "> *Ví dụ*: 'Trước đây em đôi khi quá tập trung vào tiểu tiết khiến tiến độ bị chậm lại. Sau đó em đã áp dụng phương pháp Pomodoro và đặt Deadline từng task trên Trello, hiện tại em luôn hoàn thành công việc đúng tiến độ.'\n\n"
                "### 3. 'Tại sao bạn ứng tuyển vào công ty chúng tôi?'\n"
                "- Đừng nói chung chung là 'công ty lớn'. Hãy nhắc đến **sản phẩm cụ thể**, văn hóa hoặc sứ mệnh của công ty mà bạn đã tìm hiểu kỹ.\n\n"
                "👉 Hãy vào tab **Phỏng vấn thử** để luyện tập trực tiếp với AI và nhận phản hồi chấm điểm theo thời gian thực!"
            )
            suggestions = [
                "Luyện phỏng vấn thử với AI ngay",
                "Cách đặt câu hỏi ngược lại cho nhà tuyển dụng",
                "Cách trả lời khi gặp câu hỏi kỹ thuật không biết"
            ]

        elif is_roadmap:
            intent = "roadmap_inquiry"
            matched_role = "Backend Developer"
            for r in ROLE_SKILL_TAXONOMY.keys():
                if any(k in msg_lower for k in r.lower().split()):
                    matched_role = r
                    break

            r_data = ROLE_SKILL_TAXONOMY.get(matched_role, ROLE_SKILL_TAXONOMY["Backend Developer"])
            reply = (
                f"Chào **{student_name}**, đây là Lộ trình 4 giai đoạn làm chủ vị trí **{matched_role}**:\n\n"
                f"### 🎯 Giai đoạn 1: Nền tảng cốt lõi (Tháng 1)\n"
                f"- **Kỹ năng cần học**: {', '.join(r_data['core'][:4])}\n"
                f"- **Mục tiêu**: Nắm vững cú pháp, nguyên lý hoạt động và giải thuật cơ bản.\n\n"
                f"### 🚀 Giai đoạn 2: Xây dựng Dự án Capstone (Tháng 2)\n"
                f"- **Kỹ năng thực chiến**: {', '.join(r_data['advanced'][:3])}\n"
                f"- **Sản phẩm đầu ra**: Xây dựng 1 ứng dụng hoàn chỉnh có Database, API và xử lý dữ liệu thực tế.\n\n"
                f"### 🛡️ Giai đoạn 3: Tối ưu & Mở rộng (Tháng 3)\n"
                f"- **Kỹ năng**: Clean Code, Kiểm thử tự động (Unit Test), Tối ưu hiệu năng và triển khai Cloud.\n\n"
                f"### 🏆 Giai đoạn 4: Hoàn thiện Profile & Ứng tuyển (Tháng 4)\n"
                f"- **Hành động**: Tối ưu CV chuẩn ATS, đưa code lên GitHub có README đẹp mắt, luyện Mock Interview.\n\n"
                f"👉 Bạn có thể xem lộ trình tương tác trực quan tại tab **Lộ trình kỹ năng** trên hệ thống!"
            )
            suggestions = [
                f"Tìm việc cho vị trí {matched_role}",
                "Các chứng chỉ quốc tế nên thi",
                "Phỏng vấn thử cho vị trí này"
            ]

        elif is_guidance:
            intent = "career_guidance"
            reply = (
                f"Chào **{student_name}**, việc băn khoăn về định hướng nghề nghiệp là điều rất bình thường ở thời sinh viên! Hãy cùng AI phân tích theo 3 nhóm định hướng chính:\n\n"
                "### 1. Nếu bạn yêu thích Logic, Kỹ thuật & Công nghệ:\n"
                "- **Trí tuệ nhân tạo (AI/ML)**: Phù hợp bạn giỏi toán, thống kê, thích nghiên cứu thuật toán.\n"
                "- **Kỹ sư Phần mềm (Backend/Frontend)**: Cơ hội việc làm lớn, tính ứng dụng thực tiễn cao.\n"
                "- **An toàn thông tin / Cloud**: Nhu cầu tuyển dụng ổn định, bảo mật hạ tầng số.\n\n"
                "### 2. Nếu bạn thích Dữ liệu, Kinh doanh & Chiến lược:\n"
                "- **Data Analyst / BI**: Cầu nối giữa kỹ thuật và kinh doanh, tư duy bằng số liệu.\n"
                "- **Phân tích Tài chính & Đầu tư**: Định giá, thẩm định dự án, làm việc tại ngân hàng/chứng khoán.\n"
                "- **Digital Marketing & E-commerce**: Năng động, sáng tạo nội dung, tối ưu chiến dịch quảng cáo.\n\n"
                "### 3. Nếu bạn thích Con người, Giao tiếp & Tổ chức:\n"
                "- **Quản trị Nhân sự (HR / Headhunter)**: Thu hút nhân tài, xây dựng văn hóa doanh nghiệp.\n"
                "- **Logistics & Chuỗi cung ứng**: Điều phối dòng chảy hàng hóa quốc tế, giao thương toàn cầu.\n"
                "- **Quản lý Khách sạn / Pháp chế**: Môi trường dịch vụ chuyên nghiệp, tuân thủ pháp lý.\n\n"
                "> 💬 **Hãy chia sẻ thêm với tôi**: Bạn học chuyên ngành gì và cảm thấy hứng thú nhất khi làm công việc như thế nào? Tôi sẽ gợi ý nghề nghiệp chính xác nhất cho bạn!"
            )
            suggestions = [
                "Em học CNTT nhưng không giỏi lập trình thì làm gì?",
                "Nhu cầu tuyển dụng ngành Logistics hiện nay",
                "So sánh nghề Data Analyst và AI Engineer"
            ]

        else:
            # General polite helpful response
            reply = (
                f"Xin chào **{student_name}**! Tôi là **CareerBridge AI Advisor** — Trợ lý ảo Hướng nghiệp và Phát triển Nghề nghiệp thông minh.\n\n"
                "Tôi có thể hỗ trợ bạn mọi khía cạnh trong hành trình tìm việc và xây dựng sự nghiệp:\n\n"
                "1. 🔍 **Gợi ý việc làm**: Tìm các vị trí Thực tập / Fresher đa ngành nghề từ các tập đoàn uy tín.\n"
                "2. 📄 **Tối ưu CV & Portfolio**: Hướng dẫn viết hồ sơ chuẩn ATS, công thức lượng hóa STAR.\n"
                "3. 🎙️ **Mô phỏng Phỏng vấn**: Hướng dẫn trả lời các câu hỏi tình huống, kỹ thuật và hành vi.\n"
                "4. 🗺️ **Lộ trình Kỹ năng**: Phân tích khoảng cách năng lực và lộ trình 4 giai đoạn thăng tiến.\n"
                "5. 📊 **Xu hướng Thị trường**: Tra cứu mức lương và dự báo nhu cầu nhân lực 16 ngành nghề.\n\n"
                "Bạn cần tôi hỗ trợ điều gì hôm nay?"
            )
            suggestions = [
                "Gợi ý việc làm thực tập mới nhất",
                "Tra cứu mức lương Fresher các ngành",
                "Làm sao để viết CV vượt qua vòng lọc ATS?",
                "Tư vấn định hướng nghề nghiệp cho em"
            ]

    # Persist message turn to SQLite database
    try:
        with db_session() as conn:
            cursor = conn.cursor()
            user_msg_id = f"msg_{uuid.uuid4().hex[:12]}"
            bot_msg_id = f"msg_{uuid.uuid4().hex[:12]}"

            cursor.execute("""
                INSERT INTO chat_messages (id, session_id, user_id, sender, message, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_msg_id, session_id, user_id, "user", msg_clean, json.dumps(context), now_iso))

            cursor.execute("""
                INSERT INTO chat_messages (id, session_id, user_id, sender, message, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (bot_msg_id, session_id, user_id, "assistant", reply, json.dumps({
                "intent": intent,
                "suggestions": suggestions,
                "suggested_jobs_count": len(suggested_jobs)
            }), now_iso))
    except Exception as e:
        print(f"Chat persistence error: {e}")

    return {
        "reply": reply,
        "intent": intent,
        "session_id": session_id,
        "suggestions": suggestions,
        "suggested_jobs": suggested_jobs if suggested_jobs else None,
        "created_at": now_iso
    }
