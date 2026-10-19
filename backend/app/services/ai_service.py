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
