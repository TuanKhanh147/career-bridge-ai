// Main Application Logic for CareerBridge AI

let currentUser = null;
let activeTab = 'jobs';
let mockSession = null;
let currentMockQuestionIdx = 0;

// Speech Recognition setup (Voice-to-text)
let recognition = null;
let isRecording = false;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = 'vi-VN';
}

// Toast helper
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  const bgColors = {
    success: 'bg-emerald-600 text-white',
    error: 'bg-rose-600 text-white',
    warning: 'bg-amber-600 text-white',
    info: 'bg-blue-600 text-white'
  };

  toast.className = `px-4 py-3 rounded-xl shadow-xl flex items-center space-x-2 text-sm font-medium transition-all duration-300 transform translate-y-2 opacity-0 ${bgColors[type] || bgColors.info}`;
  toast.innerHTML = `
    <span>${message}</span>
  `;

  container.appendChild(toast);
  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  });

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Initialize application
async function initApp() {
  const token = API.getToken();
  if (token) {
    try {
      currentUser = await API.getMe();
    } catch (e) {
      currentUser = null;
      API.setToken(null);
    }
  }

  // Only auto-login on initial fresh visit for showcase
  const hasVisited = localStorage.getItem('cb_has_visited');
  if (!currentUser && !hasVisited) {
    try {
      const res = await API.login('student@careerbridge.edu.vn', 'password123');
      currentUser = res.user;
      localStorage.setItem('cb_has_visited', 'true');
    } catch (e) {
      console.warn('Showcase login skipped:', e);
    }
  }

  updateNavbar();
  navigateTab(activeTab);
}

// Quick Role Switcher
async function switchRole(role) {
  const demoAccounts = {
    student: { email: 'student@careerbridge.edu.vn', password: 'password123' },
    recruiter: { email: 'recruiter@careerbridge.edu.vn', password: 'password123' },
    admin: { email: 'admin@careerbridge.edu.vn', password: 'password123' }
  };

  const cred = demoAccounts[role];
  if (!cred) return;

  try {
    const res = await API.login(cred.email, cred.password);
    currentUser = res.user;
    showToast(`Đã chuyển sang vai trò: ${getRoleBadge(currentUser.role)}`, 'success');

    // Default tab per role
    if (currentUser.role === 'student') activeTab = 'jobs';
    else if (currentUser.role === 'recruiter') activeTab = 'recruiter-jobs';
    else if (currentUser.role === 'admin') activeTab = 'admin-stats';

    updateNavbar();
    navigateTab(activeTab);
  } catch (err) {
    showToast('Lỗi chuyển vai trò: ' + err.message, 'error');
  }
}

function getRoleBadge(role) {
  if (role === 'student') return '🎓 Sinh viên';
  if (role === 'recruiter') return '🏢 Nhà tuyển dụng';
  if (role === 'admin') return '🏛️ Ban Hướng nghiệp';
  return role;
}

// Update Navbar
function updateNavbar() {
  const navContainer = document.getElementById('main-nav-links');
  const userWidget = document.getElementById('user-profile-widget');
  const roleSelector = document.getElementById('role-quick-switcher');

  if (!navContainer || !userWidget) return;

  if (roleSelector && currentUser) {
    roleSelector.innerHTML = `
      <div class="flex items-center space-x-1 text-xs bg-slate-100 p-1 rounded-xl border border-slate-200">
        <span class="text-slate-500 font-medium px-2 hidden lg:inline">Tài khoản demo:</span>
        <button onclick="switchRole('student')" class="px-2.5 py-1 rounded-lg font-medium transition ${currentUser.role === 'student' ? 'bg-white shadow text-blue-600 font-semibold' : 'text-slate-600 hover:text-slate-900'}">
          🎓 SV mẫu
        </button>
        <button onclick="switchRole('recruiter')" class="px-2.5 py-1 rounded-lg font-medium transition ${currentUser.role === 'recruiter' ? 'bg-white shadow text-blue-600 font-semibold' : 'text-slate-600 hover:text-slate-900'}">
          🏢 Doanh nghiệp
        </button>
        <button onclick="switchRole('admin')" class="px-2.5 py-1 rounded-lg font-medium transition ${currentUser.role === 'admin' ? 'bg-white shadow text-blue-600 font-semibold' : 'text-slate-600 hover:text-slate-900'}">
          🏛️ Hướng nghiệp
        </button>
      </div>
    `;
  }

  let links = [];

  if (!currentUser || currentUser.role === 'student') {
    links = [
      { id: 'jobs', label: '💼 Việc làm & Ghép nối AI' },
      { id: 'cv', label: '📄 Tối ưu CV & ATS' },
      { id: 'interview', label: '🎙️ Phỏng vấn thử AI' },
      { id: 'roadmap', label: '🗺️ Lộ trình kỹ năng' },
      { id: 'profile', label: '📁 Hồ sơ & Đơn ứng tuyển' },
    ];
  } else if (currentUser.role === 'recruiter') {
    links = [
      { id: 'recruiter-jobs', label: '📋 Quản lý tin tuyển dụng' },
      { id: 'recruiter-post', label: '➕ Đăng tin tuyển dụng' },
      { id: 'recruiter-candidates', label: '🤖 AI Tìm kiếm ứng viên' },
      { id: 'analytics-market', label: '📈 Xu hướng thị trường' },
    ];
  } else if (currentUser.role === 'admin') {
    links = [
      { id: 'admin-stats', label: '📊 Tổng quan việc làm' },
      { id: 'admin-users', label: '👥 Quản lý người dùng' },
      { id: 'admin-jobs', label: '💼 Giám sát tin tuyển dụng' },
      { id: 'analytics-market', label: '📈 Báo cáo thị trường' },
    ];
  }

  navContainer.innerHTML = links.map(l => `
    <button onclick="navigateTab('${l.id}')" class="nav-tab px-3 py-2 text-sm font-medium transition rounded-lg ${activeTab === l.id ? 'text-blue-600 bg-blue-50 font-semibold' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'}">
      ${l.label}
    </button>
  `).join('');

  if (currentUser) {
    userWidget.innerHTML = `
      <div class="flex items-center space-x-2 sm:space-x-3">
        <!-- Prominent Register Button always accessible -->
        <button onclick="openAuthModal('register-student')" class="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 text-xs font-bold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-xl transition">
          <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path></svg>
          <span>+ Đăng ký SV khác</span>
        </button>

        <div class="text-right hidden md:block">
          <div class="text-xs sm:text-sm font-semibold text-slate-800 leading-tight">${currentUser.full_name}</div>
          <div class="text-[11px] text-blue-600 font-medium">${getRoleBadge(currentUser.role)}</div>
        </div>

        <div class="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-blue-600 text-white font-bold flex items-center justify-center text-xs sm:text-sm shadow-md ring-2 ring-blue-100 cursor-pointer" onclick="navigateTab('profile')" title="Xem hồ sơ">
          ${currentUser.full_name.charAt(0)}
        </div>

        <button onclick="openAuthModal('login')" title="Chuyển tài khoản khác" class="p-1.5 text-slate-400 hover:text-blue-600 transition rounded-lg hover:bg-slate-100">
          <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path></svg>
        </button>

        <button onclick="logout()" title="Đăng xuất" class="p-1.5 text-slate-400 hover:text-rose-600 transition rounded-lg hover:bg-slate-100">
          <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
        </button>
      </div>
    `;
  } else {
    userWidget.innerHTML = `
      <div class="flex items-center space-x-2">
        <button onclick="openAuthModal('login')" class="px-3.5 py-2 text-xs sm:text-sm font-semibold text-slate-700 hover:bg-slate-100 rounded-xl transition">
          Đăng nhập
        </button>
        <button onclick="openAuthModal('register-student')" class="px-4 py-2 text-xs sm:text-sm font-bold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 rounded-xl shadow-md transition flex items-center space-x-1.5">
          <span>✨ Đăng ký Sinh viên</span>
        </button>
      </div>
    `;
  }
}

function logout() {
  API.setToken(null);
  currentUser = null;
  localStorage.setItem('cb_has_visited', 'true');
  showToast('Đã đăng xuất tài khoản', 'info');
  updateNavbar();
  navigateTab('jobs');
}

// Navigation router
function navigateTab(tabId) {
  activeTab = tabId;
  updateNavbar();

  const contentArea = document.getElementById('app-content');
  if (!contentArea) return;

  switch (tabId) {
    case 'jobs':
      renderJobsView(contentArea);
      break;
    case 'cv':
      renderCVReviewView(contentArea);
      break;
    case 'interview':
      renderMockInterviewView(contentArea);
      break;
    case 'roadmap':
      renderRoadmapView(contentArea);
      break;
    case 'profile':
      renderProfileView(contentArea);
      break;
    case 'recruiter-jobs':
      renderRecruiterJobsView(contentArea);
      break;
    case 'recruiter-post':
      renderRecruiterPostView(contentArea);
      break;
    case 'recruiter-candidates':
      renderRecruiterCandidatesView(contentArea);
      break;
    case 'admin-stats':
    case 'analytics-market':
      renderAdminStatsView(contentArea);
      break;
    case 'admin-users':
      renderAdminUsersView(contentArea);
      break;
    case 'admin-jobs':
      renderAdminJobsView(contentArea);
      break;
    default:
      renderJobsView(contentArea);
  }
}

// ==========================================
// 1. JOBS & AI MATCHING VIEW
// ==========================================
async function renderJobsView(container) {
  container.innerHTML = `
    <div class="space-y-6">
      <!-- Hero Banner -->
      <div class="gradient-hero p-6 sm:p-8 rounded-3xl border border-blue-100 shadow-sm relative overflow-hidden">
        <div class="relative z-10 max-w-3xl">
          <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-700 mb-3">
            ✨ AI Career Match Engine v1.0
          </span>
          <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Kết nối Việc làm & Thực tập phù hợp với <span class="gradient-text">Năng lực của Bạn</span>
          </h1>
          <p class="mt-2 text-slate-600 text-sm sm:text-base leading-relaxed">
            Hệ thống tự động phân tích hồ sơ năng lực (GPA, kỹ năng cứng, dự án, mục tiêu) và mô tả công việc (JD) để xếp hạng các cơ hội có tỷ lệ trúng tuyển cao nhất.
          </p>
        </div>
      </div>

      <!-- Filters & Search -->
      <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-3 items-center justify-between">
        <div class="relative w-full md:w-96">
          <input type="text" id="job-search-input" placeholder="Tìm theo chức danh, công ty, kỹ năng..."
            class="w-full pl-10 pr-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition"
            onkeyup="if(event.key === 'Enter') handleJobFilter()">
          <svg class="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        </div>

        <div class="flex flex-wrap items-center gap-2 w-full md:w-auto">
          <select id="filter-job-type" onchange="handleJobFilter()" class="text-xs sm:text-sm bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">Tất cả loại hình</option>
            <option value="Thực tập sinh (Internship)">Thực tập sinh</option>
            <option value="Mới tốt nghiệp (Fresher)">Mới tốt nghiệp (Fresher)</option>
          </select>

          <select id="filter-industry" onchange="handleJobFilter()" class="text-xs sm:text-sm bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">Tất cả ngành nghề</option>
            <option value="Công nghệ thông tin & Phần mềm">CNTT & Phần mềm</option>
            <option value="Trí tuệ nhân tạo & Dữ liệu">Trí tuệ nhân tạo & Dữ liệu</option>
            <option value="Digital Marketing & Truyền thông">Digital Marketing & Truyền thông</option>
            <option value="Tài chính, Ngân hàng & Chứng khoán">Tài chính, Ngân hàng & Chứng khoán</option>
            <option value="Kế toán & Kiểm toán">Kế toán & Kiểm toán</option>
            <option value="Logistics & Quản trị Chuỗi cung ứng">Logistics & Chuỗi cung ứng</option>
            <option value="Quản trị Nhân sự (HR)">Quản trị Nhân sự (HR)</option>
            <option value="Thiết kế Sản phẩm & UI/UX">Thiết kế Sản phẩm & UI/UX</option>
            <option value="Kỹ thuật & Tự động hóa">Kỹ thuật & Tự động hóa</option>
            <option value="An toàn thông tin & Mạng máy tính">An toàn thông tin & Mạng</option>
          </select>

          <button onclick="handleJobFilter()" class="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-semibold shadow-sm transition">
            Lọc kết quả
          </button>
        </div>
      </div>

      <!-- Jobs Grid -->
      <div id="jobs-cards-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        <div class="col-span-full py-12 text-center text-slate-400">
          <div class="animate-spin inline-block w-8 h-8 border-4 border-current border-t-transparent rounded-full text-blue-600 mb-2"></div>
          <div>Đang tính toán độ tương thích AI cho danh sách việc làm...</div>
        </div>
      </div>
    </div>
  `;

  loadJobsList();
}

async function handleJobFilter() {
  const q = document.getElementById('job-search-input')?.value || '';
  const jobType = document.getElementById('filter-job-type')?.value || '';
  const industry = document.getElementById('filter-industry')?.value || '';

  const params = {};
  if (q) params.q = q;
  if (jobType) params.job_type = jobType;
  if (industry) params.industry = industry;

  loadJobsList(params);
}

async function loadJobsList(params = {}) {
  const grid = document.getElementById('jobs-cards-grid');
  if (!grid) return;

  try {
    const jobs = await API.getJobs(params);
    if (!jobs.length) {
      grid.innerHTML = `
        <div class="col-span-full bg-white p-12 text-center rounded-2xl border border-slate-200">
          <div class="text-4xl mb-3">🔍</div>
          <h3 class="text-base font-bold text-slate-800">Không tìm thấy cơ hội phù hợp</h3>
          <p class="text-sm text-slate-500 mt-1">Hãy thử tìm kiếm với từ khóa khác hoặc bỏ các bộ lọc.</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = jobs.map(job => {
      const matchBadge = job.match_score !== null && job.match_score !== undefined ? `
        <div class="flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold ${
          job.match_score >= 88 ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' :
          job.match_score >= 75 ? 'bg-blue-100 text-blue-800 border border-blue-200' :
          job.match_score >= 60 ? 'bg-amber-100 text-amber-800 border border-amber-200' :
          'bg-slate-100 text-slate-700 border border-slate-200'
        }">
          <span>🤖 Phù hợp: ${job.match_score}%</span>
        </div>
      ` : '';

      return `
        <div class="bg-white rounded-2xl border border-slate-200 hover:border-blue-400 p-5 shadow-sm hover:shadow-md transition-all flex flex-col justify-between group">
          <div>
            <div class="flex items-start justify-between gap-2 mb-3">
              <div>
                <span class="text-xs font-semibold text-blue-600 bg-blue-50 px-2.5 py-0.5 rounded-md inline-block mb-1">
                  ${job.job_type}
                </span>
                <h3 class="font-bold text-slate-900 group-hover:text-blue-600 transition text-base leading-snug">
                  ${job.title}
                </h3>
                <p class="text-sm font-medium text-slate-600">${job.company_name}</p>
              </div>
              ${matchBadge}
            </div>

            <div class="space-y-1.5 text-xs text-slate-500 my-3">
              <div class="flex items-center space-x-2">
                <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path></svg>
                <span>${job.location}</span>
              </div>
              <div class="flex items-center space-x-2">
                <svg class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span class="font-semibold text-emerald-700">${job.salary_range}</span>
              </div>
            </div>

            <p class="text-xs text-slate-600 line-clamp-2 mb-3">
              ${job.description}
            </p>

            <div class="flex flex-wrap gap-1.5 mb-4">
              ${(job.required_skills || []).slice(0, 4).map(s => `
                <span class="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded-md font-medium">
                  ${s}
                </span>
              `).join('')}
              ${(job.required_skills || []).length > 4 ? `
                <span class="text-xs text-slate-400 self-center">+${job.required_skills.length - 4}</span>
              ` : ''}
            </div>
          </div>

          <div class="pt-3 border-t border-slate-100 flex items-center justify-between">
            <button onclick="openJobDetailModal('${job.id}')" class="w-full py-2 bg-slate-900 hover:bg-blue-600 text-white rounded-xl text-xs font-semibold transition flex items-center justify-center space-x-1.5">
              <span>Xem chi tiết & Phân tích AI</span>
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
            </button>
          </div>
        </div>
      `;
    }).join('');
  } catch (err) {
    grid.innerHTML = `
      <div class="col-span-full p-8 text-center text-rose-600 bg-rose-50 rounded-2xl">
        Lỗi khi tải danh sách việc làm: ${err.message}
      </div>
    `;
  }
}

// Modal: Job Details & AI Matching Deep-Dive
async function openJobDetailModal(jobId) {
  try {
    const job = await API.getJob(jobId);
    const modal = document.getElementById('main-modal');
    const modalContent = document.getElementById('modal-content');

    const analysis = job.match_analysis;
    const matchScore = job.match_score || (analysis ? analysis.match_score : null);

    let aiSection = '';
    if (matchScore !== null) {
      aiSection = `
        <div class="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-5 mb-6">
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-blue-200">
            <div>
              <div class="text-xs uppercase tracking-wider text-blue-600 font-bold">Kết quả phân tích trí tuệ nhân tạo</div>
              <h4 class="text-lg font-extrabold text-slate-900">Mức độ tương thích hồ sơ</h4>
            </div>
            <div class="flex items-center space-x-3 bg-white px-4 py-2 rounded-xl shadow-sm border border-blue-100">
              <div class="text-2xl font-black text-blue-600">${matchScore}%</div>
              <div class="text-xs font-semibold text-slate-600">${analysis?.fit_level || 'Phù hợp'}</div>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <!-- Strengths -->
            <div class="bg-white p-3.5 rounded-xl border border-blue-100">
              <div class="font-bold text-emerald-700 flex items-center space-x-1.5 mb-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                <span>Điểm mạnh của bạn:</span>
              </div>
              <ul class="space-y-1.5 text-slate-700">
                ${(analysis?.strengths || ['Kỹ năng phù hợp với yêu cầu cốt lõi.']).map(s => `
                  <li class="flex items-start space-x-1.5">
                    <span class="text-emerald-500 font-bold">•</span>
                    <span>${s}</span>
                  </li>
                `).join('')}
              </ul>
            </div>

            <!-- Gaps -->
            <div class="bg-white p-3.5 rounded-xl border border-blue-100">
              <div class="font-bold text-amber-700 flex items-center space-x-1.5 mb-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                <span>Kỹ năng cần bổ sung / Lưu ý:</span>
              </div>
              <ul class="space-y-1.5 text-slate-700">
                ${(analysis?.gaps || ['Cần trau dồi thêm kinh nghiệm thực chiến.']).map(g => `
                  <li class="flex items-start space-x-1.5">
                    <span class="text-amber-500 font-bold">•</span>
                    <span>${g}</span>
                  </li>
                `).join('')}
              </ul>
            </div>
          </div>

          <!-- Recommendations -->
          <div class="mt-3.5 bg-white/70 p-3 rounded-xl text-xs text-slate-700 border border-blue-100">
            <span class="font-bold text-blue-800">💡 Lời khuyên trước khi nộp đơn:</span>
            <span class="ml-1">${(analysis?.recommendations || []).join(' ')}</span>
          </div>
        </div>
      `;
    }

    modalContent.innerHTML = `
      <div class="p-6 max-h-[85vh] overflow-y-auto">
        <div class="flex items-start justify-between mb-4">
          <div>
            <span class="text-xs font-bold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-lg">${job.job_type}</span>
            <h2 class="text-xl sm:text-2xl font-black text-slate-900 mt-1">${job.title}</h2>
            <p class="text-slate-600 font-medium text-sm">${job.company_name} • ${job.location}</p>
          </div>
          <button onclick="closeModal()" class="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>

        <div class="flex flex-wrap gap-4 py-3 border-y border-slate-100 text-xs text-slate-600 mb-5">
          <div><span class="text-slate-400">Mức lương:</span> <strong class="text-emerald-700 text-sm">${job.salary_range}</strong></div>
          <div><span class="text-slate-400">Ngành nghề:</span> <strong>${job.industry}</strong></div>
          <div><span class="text-slate-400">Yêu cầu GPA:</span> <strong>${job.min_gpa ? `>= ${job.min_gpa}` : 'Không bắt buộc'}</strong></div>
        </div>

        ${aiSection}

        <div class="space-y-4 text-sm text-slate-700 leading-relaxed mb-6">
          <div>
            <h4 class="font-bold text-slate-900 mb-1">Mô tả công việc:</h4>
            <div class="whitespace-pre-line text-xs sm:text-sm bg-slate-50 p-3.5 rounded-xl border border-slate-100">${job.description}</div>
          </div>
          <div>
            <h4 class="font-bold text-slate-900 mb-1">Yêu cầu ứng viên:</h4>
            <div class="whitespace-pre-line text-xs sm:text-sm bg-slate-50 p-3.5 rounded-xl border border-slate-100">${job.requirements}</div>
          </div>
          ${job.responsibilities ? `
            <div>
              <h4 class="font-bold text-slate-900 mb-1">Trách nhiệm chính:</h4>
              <div class="whitespace-pre-line text-xs sm:text-sm bg-slate-50 p-3.5 rounded-xl border border-slate-100">${job.responsibilities}</div>
            </div>
          ` : ''}
          <div>
            <h4 class="font-bold text-slate-900 mb-1.5">Kỹ năng yêu cầu:</h4>
            <div class="flex flex-wrap gap-1.5">
              ${(job.required_skills || []).map(s => `
                <span class="text-xs bg-blue-50 text-blue-700 px-3 py-1 rounded-lg font-semibold border border-blue-100">${s}</span>
              `).join('')}
            </div>
          </div>
        </div>

        ${currentUser?.role === 'student' ? `
          <div class="border-t border-slate-200 pt-5 mt-6">
            <h4 class="font-bold text-slate-900 text-sm mb-2">Thư giới thiệu / Lời nhắn tới nhà tuyển dụng (Cover Note):</h4>
            <textarea id="apply-cover-note" rows="3" placeholder="Giới thiệu ngắn gọn lý do bạn phù hợp với vị trí này..."
              class="w-full text-xs sm:text-sm p-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none mb-3"></textarea>
            
            <div class="flex items-center justify-end space-x-3">
              <button onclick="closeModal()" class="px-4 py-2 text-xs sm:text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-xl">
                Đóng
              </button>
              <button onclick="submitApplication('${job.id}')" class="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs sm:text-sm font-bold rounded-xl shadow-md transition flex items-center space-x-2">
                <span>🚀 Nộp đơn ứng tuyển ngay</span>
              </button>
            </div>
          </div>
        ` : `
          <div class="border-t border-slate-200 pt-4 flex justify-end">
            <button onclick="closeModal()" class="px-5 py-2 text-sm font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl">
              Đóng
            </button>
          </div>
        `}
      </div>
    `;

    modal.classList.remove('hidden');
  } catch (err) {
    showToast('Lỗi tải chi tiết: ' + err.message, 'error');
  }
}

async function submitApplication(jobId) {
  const note = document.getElementById('apply-cover-note')?.value || '';
  try {
    await API.applyJob(jobId, note);
    showToast('Ứng tuyển thành công! Nhà tuyển dụng sẽ xem xét hồ sơ của bạn.', 'success');
    closeModal();
    navigateTab('profile');
  } catch (err) {
    showToast('Lỗi ứng tuyển: ' + err.message, 'error');
  }
}

function closeModal() {
  const modal = document.getElementById('main-modal');
  if (modal) modal.classList.add('hidden');
}

// ==========================================
// 2. AI CV REVIEW & ATS OPTIMIZER VIEW
// ==========================================
async function renderCVReviewView(container) {
  let profileCvText = '';
  try {
    const profile = await API.getStudentProfile();
    profileCvText = profile.cv_text || '';
  } catch (e) {}

  container.innerHTML = `
    <div class="space-y-6">
      <div class="gradient-hero p-6 sm:p-8 rounded-3xl border border-blue-100">
        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-700 mb-2">
          📄 AI CV & ATS Analyzer
        </span>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Chấm điểm ATS & Tối ưu hóa CV theo Chuẩn Quốc tế
        </h1>
        <p class="mt-2 text-slate-600 text-sm max-w-2xl">
          Công cụ AI phân tích mật độ từ khóa ngành nghề, cấu trúc đề mục, phát hiện thiếu sót và tự động viết lại các gạch đầu dòng kinh nghiệm theo mô hình <strong>STAR</strong>.
        </p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Left: Input Form -->
        <div class="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="font-bold text-slate-900 text-base">Nội dung CV của bạn</h3>
            <button onclick="loadSampleCV()" class="text-xs text-blue-600 font-semibold hover:underline">
              Nạp CV mẫu của bạn
            </button>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Vị trí mục tiêu:</label>
            <select id="cv-target-role" class="w-full text-xs sm:text-sm p-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500">
              <option value="Backend Developer">Kỹ sư Lập trình Backend (Python/Node/Java)</option>
              <option value="AI / Machine Learning Engineer">Kỹ sư Trí tuệ Nhân tạo (AI/ML)</option>
              <option value="Frontend Developer">Kỹ sư Lập trình Frontend (React/TypeScript)</option>
              <option value="Data Analyst / Business Intelligence">Chuyên viên Phân tích Dữ liệu (Data Analyst)</option>
              <option value="Mobile App Developer">Lập trình Di động (Flutter/React Native/iOS/Android)</option>
              <option value="DevOps / Cloud Engineer">Kỹ sư DevOps & Điện toán Đám mây</option>
              <option value="Cybersecurity / An toàn Thông tin">Chuyên viên An toàn Thông tin & Bảo mật (Cybersecurity)</option>
              <option value="Product Manager / Business Analyst (BA)">Chuyên viên Phân tích Nghiệp vụ (BA/PM)</option>
              <option value="Digital Marketing & Performance Media">Chuyên viên Digital Marketing & Performance Media</option>
              <option value="Financial Analyst & Phân tích Tài chính">Chuyên viên Phân tích Tài chính (Financial Analyst)</option>
              <option value="Kế toán & Kiểm toán (Auditing & Accounting)">Chuyên viên Kế toán & Kiểm toán</option>
              <option value="HR & Quản trị Nhân sự (Talent Acquisition)">Chuyên viên Tuyển dụng & Quản trị Nhân sự (HR)</option>
              <option value="Supply Chain & Quản trị Chuỗi Cung ứng (Logistics)">Quản trị Chuỗi Cung ứng & Logistics</option>
              <option value="UI/UX & Product Designer">Thiết kế Sản phẩm & Trải nghiệm (UI/UX Designer)</option>
              <option value="Kỹ sư Tự động hóa & Cơ điện tử (Automation & Robotics)">Kỹ sư Tự động hóa & Cơ điện tử</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Dán toàn bộ nội dung văn bản CV:</label>
            <textarea id="cv-text-input" rows="14" placeholder="Dán nội dung tóm tắt học vấn, kỹ năng, dự án hoặc kinh nghiệm từ CV của bạn vào đây..."
              class="w-full text-xs p-3 font-mono bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:bg-white">${profileCvText}</textarea>
          </div>

          <button onclick="analyzeCV()" id="btn-analyze-cv" class="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-xl shadow-md transition flex items-center justify-center space-x-2">
            <span>🚀 Phân tích & Tối ưu bằng AI</span>
          </button>
        </div>

        <!-- Right: Analysis Results -->
        <div class="lg:col-span-7 space-y-5" id="cv-results-container">
          <div class="bg-white p-12 text-center rounded-2xl border border-slate-200 shadow-sm text-slate-400">
            <div class="text-5xl mb-3">🤖</div>
            <h4 class="font-bold text-slate-700 text-base">Chưa có kết quả phân tích</h4>
            <p class="text-xs text-slate-500 mt-1">Hãy dán nội dung CV và nhấn nút "Phân tích & Tối ưu bằng AI" để xem điểm ATS và gợi ý cải tiến.</p>
          </div>
        </div>
      </div>
    </div>
  `;
}

function loadSampleCV() {
  const sample = `Họ và tên: Nguyễn Minh Quân
Email: student@careerbridge.edu.vn | SĐT: 0945678901 | GitHub: github.com/minhquan-dev

MỤC TIÊU NGHỀ NGHIỆP:
Trở thành Kỹ sư Backend xuất sắc, tham gia xây dựng hệ thống phần mềm hiệu năng cao phục vụ hàng triệu người dùng.

HỌC VẤN:
- Đại học Bách Khoa (2022 - 2026)
- Chuyên ngành: Khoa học Máy tính. GPA: 3.52/4.0.

KỸ NĂNG KỸ THUẬT:
- Ngôn ngữ: Python, SQL, C++.
- Framework & Tool: FastAPI, Django, Docker, Git, Redis, PostgreSQL.

DỰ ÁN NỔI BẬT:
1. Nền tảng Đặt xe thông minh EcoRide (Đồ án môn học):
- Xây dựng hệ thống REST API bằng FastAPI với kiến trúc Clean Architecture.
- Tối ưu hóa truy vấn cơ sở dữ liệu PostgreSQL và áp dụng caching với Redis, giảm thời gian phản hồi API xuống dưới 120ms.
2. Cổng thanh toán trực tuyến mô phỏng:
- Tích hợp xác thực JWT, mã hóa dữ liệu nhạy cảm và xử lý webhook giao dịch bất đồng bộ.`;

  const input = document.getElementById('cv-text-input');
  if (input) input.value = sample;
  showToast('Đã nạp nội dung CV mẫu!', 'info');
}

async function analyzeCV() {
  const text = document.getElementById('cv-text-input')?.value || '';
  const role = document.getElementById('cv-target-role')?.value || '';

  if (!text.trim()) {
    showToast('Vui lòng nhập hoặc dán nội dung CV', 'warning');
    return;
  }

  const btn = document.getElementById('btn-analyze-cv');
  const resultsContainer = document.getElementById('cv-results-container');
  if (btn) btn.disabled = true;
  if (resultsContainer) {
    resultsContainer.innerHTML = `
      <div class="bg-white p-12 text-center rounded-2xl border border-slate-200">
        <div class="animate-spin inline-block w-8 h-8 border-4 border-current border-t-transparent rounded-full text-blue-600 mb-3"></div>
        <div class="font-bold text-slate-800 text-sm">AI đang quét từ khóa ATS và kiểm tra cấu trúc...</div>
      </div>
    `;
  }

  try {
    const res = await API.reviewCV(text, role);
    renderCVAnalysisResult(res);
    showToast('Phân tích CV hoàn tất!', 'success');
  } catch (err) {
    showToast('Lỗi phân tích: ' + err.message, 'error');
  } finally {
    if (btn) btn.disabled = false;
  }
}

function renderCVAnalysisResult(data) {
  const container = document.getElementById('cv-results-container');
  if (!container) return;

  const scoreColor = data.ats_score >= 85 ? 'text-emerald-600' : data.ats_score >= 70 ? 'text-blue-600' : 'text-amber-600';
  const scoreBadgeBg = data.ats_score >= 85 ? 'bg-emerald-50 border-emerald-200' : data.ats_score >= 70 ? 'bg-blue-50 border-blue-200' : 'bg-amber-50 border-amber-200';

  container.innerHTML = `
    <!-- Top Score Banner -->
    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
      <div>
        <span class="text-xs font-bold text-slate-500 uppercase tracking-wider">Mục tiêu: ${data.target_role}</span>
        <h3 class="text-xl font-extrabold text-slate-900 mt-0.5">Điểm tương thích ATS</h3>
        <p class="text-xs text-slate-500 mt-1">Đánh giá khả năng vượt qua vòng lọc hồ sơ tự động của doanh nghiệp.</p>
      </div>

      <div class="flex items-center space-x-3 px-5 py-3 rounded-2xl border ${scoreBadgeBg}">
        <div class="text-3xl font-black ${scoreColor}">${data.ats_score}/100</div>
        <div class="text-xs font-bold text-slate-700">
          ${data.ats_score >= 85 ? '🌟 Rất ấn tượng' : data.ats_score >= 70 ? '👍 Khá tốt' : '⚠️ Cần cải thiện'}
        </div>
      </div>
    </div>

    <!-- Strengths & Weaknesses -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <h4 class="font-bold text-emerald-700 text-xs uppercase tracking-wider mb-2.5 flex items-center space-x-1.5">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
          <span>Điểm mạnh đã đạt:</span>
        </h4>
        <ul class="space-y-2 text-xs text-slate-700">
          ${(data.strengths || []).map(s => `<li class="flex items-start space-x-1.5"><span class="text-emerald-500 font-bold">✔</span><span>${s}</span></li>`).join('')}
        </ul>
      </div>

      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <h4 class="font-bold text-rose-700 text-xs uppercase tracking-wider mb-2.5 flex items-center space-x-1.5">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
          <span>Lỗ hổng & Điểm cần sửa:</span>
        </h4>
        <ul class="space-y-2 text-xs text-slate-700">
          ${(data.weaknesses || []).map(w => `<li class="flex items-start space-x-1.5"><span class="text-rose-500 font-bold">✖</span><span>${w}</span></li>`).join('')}
        </ul>
      </div>
    </div>

    <!-- Missing Keywords -->
    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
      <h4 class="font-bold text-slate-900 text-xs uppercase tracking-wider mb-2">Từ khóa ngành nghề cần bổ sung (Keywords):</h4>
      <div class="flex flex-wrap gap-2">
        ${(data.missing_keywords || []).map(k => `
          <span class="text-xs bg-amber-50 text-amber-800 border border-amber-200 px-3 py-1 rounded-lg font-medium">
            + ${k}
          </span>
        `).join('')}
      </div>
    </div>

    <!-- STAR Rewrites -->
    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
      <div class="flex items-center justify-between">
        <h4 class="font-bold text-slate-900 text-sm">Gợi ý Viết lại theo Chuẩn STAR (Trước vs Sau):</h4>
        <span class="text-xs bg-indigo-50 text-indigo-700 px-2.5 py-0.5 rounded-md font-semibold">Tăng 2.5x sức hút</span>
      </div>

      <div class="space-y-3.5">
        ${(data.bullet_rewrites || []).map((b, idx) => `
          <div class="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2 text-xs">
            <div class="text-slate-500">
              <span class="font-semibold text-rose-600">Trước (Chưa ấn tượng):</span>
              <p class="italic text-slate-600 mt-0.5">"${b.original}"</p>
            </div>
            <div class="text-slate-800 bg-white p-3 rounded-lg border border-emerald-200">
              <span class="font-bold text-emerald-700">Sau khi AI tối ưu (Chuẩn STAR):</span>
              <p class="font-medium text-slate-900 mt-0.5">"${b.improved}"</p>
            </div>
            <div class="text-slate-400 text-[11px]">
              <strong>Nguyên tắc:</strong> ${b.principle}
            </div>
          </div>
        `).join('')}
      </div>
    </div>

    <!-- Action Plan -->
    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
      <h4 class="font-bold text-slate-900 text-xs uppercase tracking-wider mb-2">Checklist hành động ngay:</h4>
      <ol class="space-y-1.5 text-xs text-slate-700 list-decimal list-inside">
        ${(data.action_recommendations || []).map(a => `<li>${a}</li>`).join('')}
      </ol>
    </div>
  `;
}

// ==========================================
// 3. AI MOCK INTERVIEW SIMULATOR VIEW
// ==========================================
function renderMockInterviewView(container) {
  mockSession = null;
  currentMockQuestionIdx = 0;

  container.innerHTML = `
    <div class="space-y-6">
      <div class="gradient-hero p-6 sm:p-8 rounded-3xl border border-blue-100">
        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-700 mb-2">
          🎙️ AI Mock Interview Simulation
        </span>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Mô phỏng Phỏng vấn Thực chiến & Phản hồi Trực tiếp
        </h1>
        <p class="mt-2 text-slate-600 text-sm max-w-2xl">
          Luyện tập trả lời các câu hỏi kỹ thuật, tình huống và hành vi (STAR Behavioral) với Trí tuệ nhân tạo. Nhận phản hồi chấm điểm theo thời gian thực kèm bài trả lời mẫu 10/10.
        </p>
      </div>

      <div id="mock-interview-stage">
        <!-- Setup Card -->
        <div class="max-w-xl mx-auto bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm space-y-5">
          <h3 class="text-lg font-bold text-slate-900 text-center">Thiết lập Phiên phỏng vấn Thử</h3>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1.5">Vị trí muốn phỏng vấn:</label>
            <select id="mock-role-input" class="w-full text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500">
              <option value="AI / Machine Learning Engineer">Kỹ sư Trí tuệ Nhân tạo (AI/ML Engineer)</option>
              <option value="Backend Developer" selected>Kỹ sư Lập trình Backend (Python/FastAPI/SQL)</option>
              <option value="Frontend Developer">Kỹ sư Lập trình Frontend (React.js/TypeScript)</option>
              <option value="Data Analyst / Business Intelligence">Chuyên viên Phân tích Dữ liệu (Data Analyst / BI)</option>
              <option value="Mobile App Developer">Lập trình Di động (Flutter/React Native/iOS/Android)</option>
              <option value="DevOps / Cloud Engineer">Kỹ sư DevOps & Điện toán Đám mây</option>
              <option value="Cybersecurity / An toàn Thông tin">Chuyên viên An toàn Thông tin & Bảo mật (Cybersecurity)</option>
              <option value="Product Manager / Business Analyst (BA)">Chuyên viên Phân tích Nghiệp vụ (BA/PM)</option>
              <option value="Digital Marketing & Performance Media">Chuyên viên Digital Marketing & Performance Media</option>
              <option value="Financial Analyst & Phân tích Tài chính">Chuyên viên Phân tích Tài chính (Financial Analyst)</option>
              <option value="Kế toán & Kiểm toán (Auditing & Accounting)">Chuyên viên Kế toán & Kiểm toán</option>
              <option value="HR & Quản trị Nhân sự (Talent Acquisition)">Chuyên viên Tuyển dụng & Quản trị Nhân sự (HR)</option>
              <option value="Supply Chain & Quản trị Chuỗi Cung ứng (Logistics)">Quản trị Chuỗi Cung ứng & Logistics</option>
              <option value="UI/UX & Product Designer">Thiết kế Sản phẩm & Trải nghiệm (UI/UX Designer)</option>
              <option value="Kỹ sư Tự động hóa & Cơ điện tử (Automation & Robotics)">Kỹ sư Tự động hóa & Cơ điện tử</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1.5">Cấp độ phỏng vấn:</label>
            <select id="mock-diff-input" class="w-full text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500">
              <option value="Thực tập sinh (Internship)">Thực tập sinh (Internship)</option>
              <option value="Mới tốt nghiệp (Fresher)" selected>Mới tốt nghiệp (Fresher / Junior)</option>
            </select>
          </div>

          <div class="bg-blue-50 p-4 rounded-xl border border-blue-100 text-xs text-blue-800 space-y-1">
            <div class="font-bold">✨ Quy trình mô phỏng:</div>
            <div>• Bộ câu hỏi gồm 3 vòng: Kiến thức kỹ thuật, Thiết kế tình huống, Phản ứng hành vi.</div>
            <div>• Hỗ trợ gõ bàn phím hoặc nói trực tiếp bằng Micro 🎙️ (Voice Speech-to-Text).</div>
            <div>• Nhận điểm số chi tiết: Mạch lạc, Độ sâu kỹ thuật, Cấu trúc STAR, Độ tự tin.</div>
          </div>

          <button onclick="startMockSession()" id="btn-start-mock" class="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-xl shadow-md transition flex items-center justify-center space-x-2">
            <span>Bắt đầu Phỏng vấn ngay</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
          </button>
        </div>
      </div>
    </div>
  `;
}

async function startMockSession() {
  const role = document.getElementById('mock-role-input')?.value || 'Backend Developer';
  const diff = document.getElementById('mock-diff-input')?.value || 'Fresher';

  const btn = document.getElementById('btn-start-mock');
  if (btn) btn.disabled = true;

  try {
    const res = await API.startMockInterview(role, diff);
    mockSession = res;
    currentMockQuestionIdx = 0;
    renderCurrentMockQuestion();
  } catch (err) {
    showToast('Lỗi khởi tạo phỏng vấn: ' + err.message, 'error');
    if (btn) btn.disabled = false;
  }
}

function renderCurrentMockQuestion() {
  const stage = document.getElementById('mock-interview-stage');
  if (!stage || !mockSession) return;

  const q = mockSession.questions[currentMockQuestionIdx];
  const total = mockSession.total_questions;

  stage.innerHTML = `
    <div class="max-w-3xl mx-auto space-y-5">
      <!-- Progress Bar -->
      <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <span class="text-xs font-bold text-slate-500">Phỏng vấn viên AI: ${mockSession.role_title}</span>
          <div class="text-sm font-bold text-blue-600">Câu hỏi ${currentMockQuestionIdx + 1} / ${total}</div>
        </div>
        <div class="w-32 bg-slate-100 rounded-full h-2.5 overflow-hidden">
          <div class="bg-blue-600 h-2.5 rounded-full transition-all duration-300" style="width: ${((currentMockQuestionIdx + 1) / total) * 100}%"></div>
        </div>
      </div>

      <!-- Question Card -->
      <div class="bg-white p-6 sm:p-7 rounded-2xl border border-blue-200 shadow-sm space-y-4">
        <div class="flex items-center space-x-2">
          <span class="px-2.5 py-0.5 rounded-md text-xs font-bold bg-blue-100 text-blue-700">${q.type}</span>
        </div>
        <h3 class="text-lg sm:text-xl font-extrabold text-slate-900 leading-snug">
          "${q.question}"
        </h3>

        <!-- Hints accordion -->
        <details class="text-xs text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-200">
          <summary class="font-semibold cursor-pointer text-blue-600">Xem gợi ý trọng tâm trả lời</summary>
          <ul class="mt-2 space-y-1 list-disc list-inside">
            ${(q.hints || []).map(h => `<li>${h}</li>`).join('')}
          </ul>
        </details>
      </div>

      <!-- Answer Input -->
      <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div class="flex items-center justify-between">
          <label class="text-xs font-bold text-slate-700">Câu trả lời của bạn:</label>
          ${recognition ? `
            <button onclick="toggleVoiceRecording()" id="btn-voice-rec" class="text-xs flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-700 transition">
              <span id="voice-rec-dot" class="w-2.5 h-2.5 rounded-full bg-slate-400"></span>
              <span id="voice-rec-text">Nói bằng Micro 🎙️</span>
            </button>
          ` : ''}
        </div>

        <textarea id="mock-answer-text" rows="6" placeholder="Gõ câu trả lời của bạn (hoặc nhấn 'Nói bằng Micro' để nói tiếng Việt)..."
          class="w-full text-xs sm:text-sm p-4 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:bg-white"></textarea>

        <div class="flex items-center justify-between pt-2">
          <button onclick="sampleAnswerFill()" class="text-xs text-blue-600 hover:underline font-semibold">
            Điền câu trả lời mẫu tham khảo
          </button>

          <button onclick="submitMockQuestionAnswer()" id="btn-submit-mock-ans" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs sm:text-sm rounded-xl shadow-md transition flex items-center space-x-2">
            <span>Gửi câu trả lời & Chấm điểm</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
          </button>
        </div>
      </div>

      <div id="mock-feedback-slot"></div>
    </div>
  `;
}

function sampleAnswerFill() {
  const textarea = document.getElementById('mock-answer-text');
  if (!textarea || !mockSession) return;
  const q = mockSession.questions[currentMockQuestionIdx];

  if (q.type.includes('Kỹ thuật')) {
    textarea.value = 'Index trong cơ sở dữ liệu hoạt động giống như mục lục của một cuốn sách. Cơ sở dữ liệu thường sử dụng cấu trúc B-Tree để lưu trữ các giá trị chỉ mục có thứ tự, giúp giảm độ phức tạp tìm kiếm từ O(N) quét toàn bộ bảng (Table Scan) xuống O(log N). Nhờ vậy các câu lệnh SELECT và WHERE chạy cực kỳ nhanh. Tuy nhiên, nếu đánh quá nhiều Index, mỗi khi thực hiện INSERT, UPDATE hay DELETE, hệ thống phải cập nhật lại tất cả cây chỉ mục, dẫn đến giảm hiệu năng ghi dữ liệu và tốn dung lượng ổ đĩa.';
  } else if (q.type.includes('Tình huống')) {
    textarea.value = 'Khi gặp tình trạng quá tải hàng chục nghìn lượt truy cập đồng thời, em sẽ áp dụng kiến trúc nhiều lớp. Thứ nhất, áp dụng Caching dữ liệu đọc bằng Redis và Connection Pooling cho Database. Thứ hai, đối với các tác vụ ghi nặng như lưu đơn ứng tuyển, em sẽ sử dụng Message Queue như RabbitMQ hoặc Kafka để đệm yêu cầu bất đồng bộ (Asynchronous processing). Thứ ba, thiết lập Rate Limiting tại API Gateway để bảo vệ backend khỏi bị sập do request dồn dập.';
  } else {
    textarea.value = 'Trong dự án tốt nghiệp, khi nhóm em bất đồng về việc lựa chọn giữa Django và FastAPI, em đã không tranh cãi cảm tính mà đề xuất cả hai bạn cùng xây dựng một prototype nhỏ (POC) với cùng 1 chức năng API và benchmark số liệu RPS cũng như độ trễ (latency). Kết quả cho thấy FastAPI đáp ứng tốc độ phản hồi nhanh hơn gấp 2 lần và tốn ít RAM hơn. Cả nhóm đã hoàn toàn đồng thuận và hoàn thành dự án xuất sắc.';
  }
}

function toggleVoiceRecording() {
  if (!recognition) return;
  const dot = document.getElementById('voice-rec-dot');
  const text = document.getElementById('voice-rec-text');
  const textarea = document.getElementById('mock-answer-text');

  if (!isRecording) {
    recognition.start();
    isRecording = true;
    if (dot) dot.className = 'w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping';
    if (text) text.innerText = 'Đang nghe bạn nói... 🔴';

    recognition.onresult = (event) => {
      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        }
      }
      if (finalTranscript && textarea) {
        textarea.value += (textarea.value ? ' ' : '') + finalTranscript;
      }
    };

    recognition.onerror = () => {
      isRecording = false;
      if (dot) dot.className = 'w-2.5 h-2.5 rounded-full bg-slate-400';
      if (text) text.innerText = 'Nói bằng Micro 🎙️';
    };
  } else {
    recognition.stop();
    isRecording = false;
    if (dot) dot.className = 'w-2.5 h-2.5 rounded-full bg-slate-400';
    if (text) text.innerText = 'Nói bằng Micro 🎙️';
  }
}

async function submitMockQuestionAnswer() {
  const ans = document.getElementById('mock-answer-text')?.value || '';
  if (!ans.trim()) {
    showToast('Vui lòng trả lời câu hỏi trước khi chấm điểm', 'warning');
    return;
  }

  const btn = document.getElementById('btn-submit-mock-ans');
  const slot = document.getElementById('mock-feedback-slot');
  if (btn) btn.disabled = true;

  if (slot) {
    slot.innerHTML = `
      <div class="bg-white p-6 rounded-2xl border border-slate-200 text-center">
        <div class="animate-spin inline-block w-6 h-6 border-3 border-current border-t-transparent rounded-full text-blue-600 mb-2"></div>
        <div class="text-xs font-semibold text-slate-700">AI đang đánh giá độ mạch lạc, tính chuyên môn và phương pháp STAR...</div>
      </div>
    `;
  }

  try {
    const res = await API.submitMockAnswer(mockSession.id, currentMockQuestionIdx, ans);
    renderMockFeedback(res);
  } catch (err) {
    showToast('Lỗi gửi câu trả lời: ' + err.message, 'error');
  } finally {
    if (btn) btn.disabled = false;
  }
}

function renderMockFeedback(data) {
  const slot = document.getElementById('mock-feedback-slot');
  if (!slot) return;

  const evalData = data.evaluation;
  const isCompleted = data.is_completed;

  slot.innerHTML = `
    <div class="bg-white p-6 sm:p-7 rounded-2xl border border-emerald-200 shadow-md space-y-5 animate-fadeIn">
      <!-- Header Score -->
      <div class="flex items-center justify-between pb-3 border-b border-slate-100">
        <div>
          <span class="text-xs font-bold text-emerald-600 uppercase">Đánh giá của AI</span>
          <h4 class="text-base font-extrabold text-slate-900">Điểm số câu trả lời này</h4>
        </div>
        <div class="text-3xl font-black text-emerald-600 bg-emerald-50 px-4 py-1.5 rounded-xl border border-emerald-200">
          ${evalData.score}/10
        </div>
      </div>

      <!-- 4 Criteria Radar-like bars -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div class="bg-slate-50 p-2.5 rounded-xl border border-slate-200 text-center">
          <div class="text-slate-500 font-medium">Mạch lạc</div>
          <div class="font-black text-slate-800 text-sm mt-0.5">${evalData.criteria_scores.clarity}/10</div>
        </div>
        <div class="bg-slate-50 p-2.5 rounded-xl border border-slate-200 text-center">
          <div class="text-slate-500 font-medium">Chuyên môn</div>
          <div class="font-black text-slate-800 text-sm mt-0.5">${evalData.criteria_scores.technical_depth}/10</div>
        </div>
        <div class="bg-slate-50 p-2.5 rounded-xl border border-slate-200 text-center">
          <div class="text-slate-500 font-medium">Chuẩn STAR</div>
          <div class="font-black text-slate-800 text-sm mt-0.5">${evalData.criteria_scores.star_method}/10</div>
        </div>
        <div class="bg-slate-50 p-2.5 rounded-xl border border-slate-200 text-center">
          <div class="text-slate-500 font-medium">Độ tự tin</div>
          <div class="font-black text-slate-800 text-sm mt-0.5">${evalData.criteria_scores.confidence}/10</div>
        </div>
      </div>

      <!-- Strengths & Improvements -->
      <div class="space-y-2 text-xs">
        <div>
          <strong class="text-emerald-700">Điểm sáng:</strong>
          <span class="text-slate-700 ml-1">${evalData.strengths.join(' ')}</span>
        </div>
        <div>
          <strong class="text-amber-700">Điểm cần nâng cấp:</strong>
          <span class="text-slate-700 ml-1">${evalData.improvements.join(' ')}</span>
        </div>
      </div>

      <!-- Model Answer -->
      <div class="bg-blue-50 p-4 rounded-xl border border-blue-200 text-xs">
        <strong class="text-blue-900 block mb-1">💡 Gợi ý câu trả lời mẫu đạt điểm 10/10:</strong>
        <p class="text-slate-700 whitespace-pre-line">${evalData.ideal_answer_model}</p>
      </div>

      <!-- Next Action -->
      <div class="pt-2 flex justify-end">
        ${!isCompleted ? `
          <button onclick="nextMockQuestion()" class="px-6 py-2.5 bg-slate-900 hover:bg-blue-600 text-white font-bold text-xs sm:text-sm rounded-xl shadow transition flex items-center space-x-2">
            <span>Tiếp tục sang câu hỏi ${currentMockQuestionIdx + 2}</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path></svg>
          </button>
        ` : `
          <div class="w-full text-center py-4 bg-emerald-50 rounded-xl border border-emerald-200">
            <h4 class="font-extrabold text-emerald-800 text-base">🎉 Bạn đã hoàn thành toàn bộ buổi phỏng vấn!</h4>
            <p class="text-xs text-slate-600 mt-1">Điểm tổng kết phiên phỏng vấn: <strong class="text-emerald-700">${data.overall_score}/10</strong></p>
            <button onclick="renderMockInterviewView(document.getElementById('app-content'))" class="mt-3 px-5 py-2 bg-emerald-600 text-white font-bold text-xs rounded-xl shadow">
              Tạo phiên luyện tập mới
            </button>
          </div>
        `}
      </div>
    </div>
  `;
}

function nextMockQuestion() {
  currentMockQuestionIdx++;
  renderCurrentMockQuestion();
}

// ==========================================
// 4. AI SKILL GAP ROADMAP VIEW
// ==========================================
function renderRoadmapView(container) {
  container.innerHTML = `
    <div class="space-y-6">
      <div class="gradient-hero p-6 sm:p-8 rounded-3xl border border-blue-100">
        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700 mb-2">
          🗺️ AI Skill Gap & Career Roadmap
        </span>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Phân tích Khoảng cách Kỹ năng & Lộ trình Học tập
        </h1>
        <p class="mt-2 text-slate-600 text-sm max-w-2xl">
          So sánh năng lực hiện có của bạn với tiêu chuẩn tuyển dụng ngành. Nhận lộ trình 4 giai đoạn cụ thể để sẵn sàng 100% ứng tuyển mục tiêu mơ ước.
        </p>
      </div>

      <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center gap-4">
        <div class="flex-1 w-full">
          <label class="block text-xs font-semibold text-slate-700 mb-1">Chọn Mục tiêu Nghề nghiệp của bạn:</label>
          <select id="roadmap-target-role" class="w-full text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500">
            <option value="Backend Developer">Kỹ sư Lập trình Backend (Python/FastAPI/Cloud)</option>
            <option value="AI / Machine Learning Engineer">Kỹ sư Trí tuệ Nhân tạo & MLOps</option>
            <option value="Frontend Developer">Kỹ sư Lập trình Frontend Hiện đại (React/Next.js)</option>
            <option value="Data Analyst / Business Intelligence">Chuyên viên Phân tích Dữ liệu (BI/Data Analyst)</option>
            <option value="Mobile App Developer">Lập trình Di động (Flutter/React Native/iOS/Android)</option>
            <option value="DevOps / Cloud Engineer">Kỹ sư DevOps & Cloud Computing</option>
            <option value="Cybersecurity / An toàn Thông tin">Chuyên viên An toàn Thông tin & Bảo mật (Cybersecurity)</option>
            <option value="Product Manager / Business Analyst (BA)">Chuyên viên Phân tích Nghiệp vụ (BA/PM)</option>
            <option value="Digital Marketing & Performance Media">Chuyên viên Digital Marketing & Performance Media</option>
            <option value="Financial Analyst & Phân tích Tài chính">Chuyên viên Phân tích Tài chính (Financial Analyst)</option>
            <option value="Kế toán & Kiểm toán (Auditing & Accounting)">Chuyên viên Kế toán & Kiểm toán</option>
            <option value="HR & Quản trị Nhân sự (Talent Acquisition)">Chuyên viên Tuyển dụng & Quản trị Nhân sự (HR)</option>
            <option value="Supply Chain & Quản trị Chuỗi Cung ứng (Logistics)">Quản trị Chuỗi Cung ứng & Logistics</option>
            <option value="UI/UX & Product Designer">Thiết kế Sản phẩm & Trải nghiệm (UI/UX Designer)</option>
            <option value="Kỹ sư Tự động hóa & Cơ điện tử (Automation & Robotics)">Kỹ sư Tự động hóa & Cơ điện tử</option>
          </select>
        </div>

        <button onclick="generateRoadmap()" id="btn-gen-roadmap" class="w-full sm:w-auto px-6 py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-xl shadow-md transition self-end">
          🚀 Tạo Lộ trình Cá nhân hóa
        </button>
      </div>

      <div id="roadmap-results-slot"></div>
    </div>
  `;

  // Auto generate first time
  generateRoadmap();
}

async function generateRoadmap() {
  const role = document.getElementById('roadmap-target-role')?.value || 'Backend Developer';
  const slot = document.getElementById('roadmap-results-slot');
  if (!slot) return;

  slot.innerHTML = `
    <div class="bg-white p-12 text-center rounded-2xl border border-slate-200 shadow-sm">
      <div class="animate-spin inline-block w-8 h-8 border-4 border-current border-t-transparent rounded-full text-blue-600 mb-2"></div>
      <div class="text-sm font-bold text-slate-700">Đang đối chiếu taxonomy kỹ năng ngành nghề và thiết lập lộ trình...</div>
    </div>
  `;

  try {
    const res = await API.generateRoadmap(role);
    renderRoadmapContent(res);
  } catch (err) {
    slot.innerHTML = `
      <div class="p-6 bg-rose-50 text-rose-600 rounded-2xl border border-rose-200 text-sm">
        Lỗi tạo lộ trình: ${err.message}
      </div>
    `;
  }
}

function renderRoadmapContent(data) {
  const slot = document.getElementById('roadmap-results-slot');
  if (!slot) return;

  slot.innerHTML = `
    <div class="space-y-6">
      <!-- Readiness Banner -->
      <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-5">
        <div>
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Mục tiêu nghề nghiệp</span>
          <h3 class="text-xl font-extrabold text-slate-900 mt-0.5">${data.target_role}</h3>
          <p class="text-xs text-slate-500 mt-1">Dựa trên bộ kỹ năng hiện tại trong hồ sơ sinh viên của bạn.</p>
        </div>

        <div class="flex items-center space-x-4 bg-slate-50 px-5 py-3 rounded-2xl border border-slate-200">
          <div>
            <div class="text-xs font-bold text-slate-500">Mức độ sẵn sàng:</div>
            <div class="text-2xl font-black text-blue-600">${data.readiness_percentage}%</div>
          </div>
          <div class="w-24 bg-slate-200 rounded-full h-3">
            <div class="bg-blue-600 h-3 rounded-full" style="width: ${data.readiness_percentage}%"></div>
          </div>
        </div>
      </div>

      <!-- Missing Skills Tags -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <h4 class="font-bold text-slate-900 text-xs uppercase tracking-wider mb-2.5">Kỹ năng quan trọng cần bổ sung (Gaps):</h4>
        <div class="flex flex-wrap gap-2">
          ${(data.missing_skills || []).map(s => `
            <span class="text-xs bg-amber-50 text-amber-800 border border-amber-200 px-3 py-1 rounded-lg font-semibold">
              ⚡ ${s}
            </span>
          `).join('')}
        </div>
      </div>

      <!-- 4 Stages Timeline -->
      <div class="space-y-4">
        ${(data.milestones || []).map((m, idx) => `
          <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-300 transition space-y-3 relative overflow-hidden">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-blue-600 bg-blue-50 px-3 py-1 rounded-md">
                ${m.phase}
              </span>
              <span class="text-xs font-semibold text-slate-400">Giai đoạn ${idx + 1}/4</span>
            </div>

            <h4 class="font-extrabold text-slate-900 text-base">${m.goal}</h4>

            <div class="text-xs text-slate-700 space-y-1.5">
              <strong class="text-slate-900 block">Nhiệm vụ trọng tâm:</strong>
              <ul class="space-y-1 list-disc list-inside">
                ${(m.actions || []).map(a => `<li>${a}</li>`).join('')}
              </ul>
            </div>

            <div class="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-slate-100 text-xs">
              <div class="flex items-center space-x-1.5 text-slate-500">
                <span>Kỹ năng thu nạp:</span>
                <span class="font-semibold text-slate-800">${(m.skills || []).join(', ')}</span>
              </div>
              <div class="text-blue-600 font-medium">
                📚 ${m.resources}
              </div>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

// ==========================================
// 5. STUDENT PROFILE & APPLICATIONS VIEW
// ==========================================
async function renderProfileView(container) {
  let profile = {};
  let applications = [];

  try {
    profile = await API.getStudentProfile();
    applications = await API.getMyApplications();
  } catch (e) {}

  container.innerHTML = `
    <div class="space-y-6">
      <div class="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div class="flex items-center space-x-4">
          <div class="w-16 h-16 rounded-2xl bg-blue-600 text-white font-extrabold text-2xl flex items-center justify-center shadow-md">
            ${currentUser?.full_name?.charAt(0) || 'U'}
          </div>
          <div>
            <h2 class="text-xl sm:text-2xl font-black text-slate-900">${currentUser?.full_name}</h2>
            <p class="text-xs sm:text-sm text-slate-500">${currentUser?.university} • ${currentUser?.major} (Khóa ${currentUser?.graduation_year})</p>
            <div class="text-xs text-emerald-600 font-semibold mt-1">GPA: ${profile.gpa || 3.5}/4.0 • Email: ${currentUser?.email}</div>
          </div>
        </div>

        <div class="flex items-center space-x-2">
          <button onclick="saveStudentProfile()" class="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs sm:text-sm font-bold rounded-xl shadow-md transition">
            Lưu thay đổi hồ sơ
          </button>
        </div>
      </div>

      <!-- Tabs: Hồ sơ vs Đơn ứng tuyển -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Left: Profile Form -->
        <div class="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <h3 class="font-bold text-slate-900 text-base pb-2 border-b border-slate-100">Hồ sơ Năng lực (Competency Profile)</h3>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Điểm GPA (Hệ 4.0):</label>
              <input type="number" step="0.01" id="profile-gpa" value="${profile.gpa || 3.5}"
                class="w-full text-xs sm:text-sm p-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500">
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Số điện thoại:</label>
              <input type="text" id="profile-phone" value="${currentUser?.phone || ''}"
                class="w-full text-xs sm:text-sm p-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500">
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Kỹ năng kỹ thuật (phân cách bằng dấu phẩy):</label>
            <input type="text" id="profile-skills" value="${(profile.skills || []).join(', ')}"
              class="w-full text-xs sm:text-sm p-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500">
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Mục tiêu nghề nghiệp (Dream Roles):</label>
            <input type="text" id="profile-roles" value="${(profile.dream_roles || []).join(', ')}"
              class="w-full text-xs sm:text-sm p-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500">
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Chứng chỉ & Giải thưởng:</label>
            <input type="text" id="profile-certs" value="${(profile.certifications || []).join(', ')}"
              class="w-full text-xs sm:text-sm p-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500">
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Văn bản CV dùng để đối sánh AI:</label>
            <textarea id="profile-cv-text" rows="8" class="w-full text-xs p-3 font-mono bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500">${profile.cv_text || ''}</textarea>
          </div>
        </div>

        <!-- Right: Applications Tracker -->
        <div class="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div class="flex items-center justify-between pb-2 border-b border-slate-100">
            <h3 class="font-bold text-slate-900 text-base">Đơn ứng tuyển đã nộp (${applications.length})</h3>
          </div>

          <div class="space-y-3 max-h-[600px] overflow-y-auto">
            ${applications.length ? applications.map(app => {
              const statusColors = {
                applied: 'bg-blue-100 text-blue-800',
                reviewing: 'bg-amber-100 text-amber-800',
                interview_scheduled: 'bg-purple-100 text-purple-800',
                accepted: 'bg-emerald-100 text-emerald-800',
                rejected: 'bg-rose-100 text-rose-800'
              };
              const statusLabels = {
                applied: 'Đã nộp đơn',
                reviewing: 'Đang xem xét',
                interview_scheduled: 'Mời phỏng vấn 🎉',
                accepted: 'Trúng tuyển 🌟',
                rejected: 'Chưa phù hợp'
              };

              return `
                <div class="p-4 rounded-xl border border-slate-200 hover:border-blue-300 transition space-y-2 bg-slate-50">
                  <div class="flex items-start justify-between gap-2">
                    <div>
                      <h4 class="font-bold text-slate-900 text-sm">${app.job?.title || 'Vị trí thực tập'}</h4>
                      <p class="text-xs text-slate-500">${app.job?.company_name || 'Doanh nghiệp'}</p>
                    </div>
                    <span class="text-xs font-bold px-2.5 py-0.5 rounded-full ${statusColors[app.status] || 'bg-slate-200'}">
                      ${statusLabels[app.status] || app.status}
                    </span>
                  </div>

                  <div class="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-200/60">
                    <span>Độ tương thích AI: <strong class="text-blue-600">${app.match_score}%</strong></span>
                    <span>${new Date(app.applied_at).toLocaleDateString('vi-VN')}</span>
                  </div>
                </div>
              `;
            }).join('') : `
              <div class="text-center py-12 text-slate-400 text-xs">
                Bạn chưa nộp đơn vị trí nào. Hãy khám phá mục "Việc làm & Ghép nối AI"!
              </div>
            `}
          </div>
        </div>
      </div>
    </div>
  `;
}

async function saveStudentProfile() {
  const gpa = parseFloat(document.getElementById('profile-gpa')?.value || 3.5);
  const skills = (document.getElementById('profile-skills')?.value || '').split(',').map(s => s.trim()).filter(Boolean);
  const dream_roles = (document.getElementById('profile-roles')?.value || '').split(',').map(s => s.trim()).filter(Boolean);
  const certifications = (document.getElementById('profile-certs')?.value || '').split(',').map(s => s.trim()).filter(Boolean);
  const cv_text = document.getElementById('profile-cv-text')?.value || '';

  try {
    await API.updateStudentProfile({
      gpa,
      skills,
      dream_roles,
      certifications,
      cv_text
    });
    showToast('Đã lưu hồ sơ năng lực thành công!', 'success');
  } catch (err) {
    showToast('Lỗi lưu hồ sơ: ' + err.message, 'error');
  }
}

// ==========================================
// 6. RECRUITER PORTAL VIEWS
// ==========================================
async function renderRecruiterJobsView(container) {
  let jobs = [];
  try {
    jobs = await API.getJobs();
  } catch (e) {}

  container.innerHTML = `
    <div class="space-y-6">
      <div class="gradient-hero p-6 sm:p-8 rounded-3xl border border-blue-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-700 mb-2">
            🏢 Cổng Thông tin Tuyển dụng Doanh nghiệp
          </span>
          <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Quản lý Tin tuyển dụng & Hồ sơ Ứng viên
          </h1>
          <p class="mt-1 text-slate-600 text-sm">
            Tận dụng AI để tự động xếp hạng ứng viên theo độ tương thích với JD của bạn.
          </p>
        </div>

        <button onclick="navigateTab('recruiter-post')" class="px-5 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs sm:text-sm rounded-xl shadow-md transition flex items-center space-x-2">
          <span>➕ Đăng tin tuyển dụng mới</span>
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        ${jobs.map(job => `
          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between space-y-4">
            <div>
              <div class="flex items-start justify-between">
                <span class="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">${job.job_type}</span>
                <span class="text-xs text-slate-400">${new Date(job.created_at).toLocaleDateString('vi-VN')}</span>
              </div>
              <h3 class="font-bold text-slate-900 text-base mt-2">${job.title}</h3>
              <p class="text-xs text-slate-500">${job.location} • ${job.salary_range}</p>

              <div class="flex flex-wrap gap-1 mt-3">
                ${(job.required_skills || []).map(s => `
                  <span class="text-[11px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-medium">${s}</span>
                `).join('')}
              </div>
            </div>

            <div class="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
              <button onclick="viewJobApplicationsModal('${job.id}')" class="flex-1 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold transition text-center">
                Xem ứng viên nộp đơn
              </button>
              <button onclick="viewAiMatchedCandidatesModal('${job.id}')" class="py-2 px-3 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-xl text-xs font-semibold transition" title="AI quét tìm ứng viên toàn trường">
                🤖 AI Tìm ứng viên
              </button>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

function renderRecruiterPostView(container) {
  container.innerHTML = `
    <div class="max-w-2xl mx-auto bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-5">
      <h2 class="text-xl font-black text-slate-900 pb-2 border-b border-slate-100">Đăng tin Tuyển dụng Mới</h2>

      <div>
        <label class="block text-xs font-semibold text-slate-700 mb-1">Tiêu đề vị trí tuyển dụng:</label>
        <input type="text" id="post-title" placeholder="VD: Thực tập sinh Kỹ sư Trí tuệ Nhân tạo (AI Intern)"
          class="w-full text-xs sm:text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500">
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label class="block text-xs font-semibold text-slate-700 mb-1">Tên công ty / Doanh nghiệp:</label>
          <input type="text" id="post-company" value="Tập đoàn Công nghệ FPT"
            class="w-full text-xs sm:text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500">
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-700 mb-1">Địa điểm làm việc:</label>
          <input type="text" id="post-location" placeholder="Hà Nội / TP.HCM / Remote"
            class="w-full text-xs sm:text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500">
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div>
          <label class="block text-xs font-semibold text-slate-700 mb-1">Loại hình:</label>
          <select id="post-type" class="w-full text-xs p-3 bg-slate-50 border border-slate-200 rounded-xl">
            <option value="Thực tập sinh (Internship)">Thực tập sinh (Internship)</option>
            <option value="Mới tốt nghiệp (Fresher)">Mới tốt nghiệp (Fresher)</option>
            <option value="Toàn thời gian (Full-time)">Toàn thời gian (Full-time)</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-700 mb-1">Mức lương:</label>
          <input type="text" id="post-salary" placeholder="8.000.000 - 15.000.000 VNĐ"
            class="w-full text-xs p-3 bg-slate-50 border border-slate-200 rounded-xl">
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-700 mb-1">Yêu cầu GPA tối thiểu:</label>
          <input type="number" step="0.1" id="post-gpa" value="2.8"
            class="w-full text-xs p-3 bg-slate-50 border border-slate-200 rounded-xl">
        </div>
      </div>

      <div>
        <label class="block text-xs font-semibold text-slate-700 mb-1">Ngành nghề:</label>
        <select id="post-industry" class="w-full text-xs p-3 bg-slate-50 border border-slate-200 rounded-xl">
          <option value="Công nghệ thông tin & Phần mềm">Công nghệ thông tin & Phần mềm</option>
          <option value="Trí tuệ nhân tạo & Dữ liệu">Trí tuệ nhân tạo & Dữ liệu</option>
          <option value="Digital Marketing & Truyền thông">Digital Marketing & Truyền thông</option>
          <option value="Tài chính, Ngân hàng & Chứng khoán">Tài chính, Ngân hàng & Chứng khoán</option>
          <option value="Kế toán & Kiểm toán">Kế toán & Kiểm toán</option>
          <option value="Logistics & Quản trị Chuỗi cung ứng">Logistics & Quản trị Chuỗi cung ứng</option>
          <option value="Quản trị Nhân sự (HR)">Quản trị Nhân sự (HR)</option>
          <option value="Thiết kế Sản phẩm & UI/UX">Thiết kế Sản phẩm & UI/UX</option>
          <option value="Kỹ thuật & Tự động hóa">Kỹ thuật & Tự động hóa</option>
          <option value="An toàn thông tin & Mạng máy tính">An toàn thông tin & Mạng máy tính</option>
        </select>
      </div>

      <div>
        <label class="block text-xs font-semibold text-slate-700 mb-1">Kỹ năng yêu cầu (phân cách bằng dấu phẩy):</label>
        <input type="text" id="post-skills" placeholder="Python, FastAPI, SQL, Docker, Git"
          class="w-full text-xs sm:text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500">
      </div>

      <div>
        <label class="block text-xs font-semibold text-slate-700 mb-1">Mô tả công việc (Job Description):</label>
        <textarea id="post-desc" rows="4" class="w-full text-xs p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500"></textarea>
      </div>

      <div>
        <label class="block text-xs font-semibold text-slate-700 mb-1">Yêu cầu ứng viên:</label>
        <textarea id="post-req" rows="4" class="w-full text-xs p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500"></textarea>
      </div>

      <div class="flex items-center justify-end space-x-3 pt-3">
        <button onclick="navigateTab('recruiter-jobs')" class="px-5 py-2.5 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl">
          Hủy
        </button>
        <button onclick="submitNewJob()" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs sm:text-sm rounded-xl shadow transition">
          🚀 Xuất bản tin tuyển dụng
        </button>
      </div>
    </div>
  `;
}

async function submitNewJob() {
  const title = document.getElementById('post-title')?.value || '';
  const company_name = document.getElementById('post-company')?.value || '';
  const location = document.getElementById('post-location')?.value || '';
  const job_type = document.getElementById('post-type')?.value || '';
  const salary_range = document.getElementById('post-salary')?.value || '';
  const industry = document.getElementById('post-industry')?.value || '';
  const min_gpa = parseFloat(document.getElementById('post-gpa')?.value || 0.0);
  const skills = (document.getElementById('post-skills')?.value || '').split(',').map(s => s.trim()).filter(Boolean);
  const description = document.getElementById('post-desc')?.value || '';
  const requirements = document.getElementById('post-req')?.value || '';

  if (!title || !company_name || !location) {
    showToast('Vui lòng điền đủ tiêu đề, công ty và địa điểm', 'warning');
    return;
  }

  try {
    await API.createJob({
      title,
      company_name,
      location,
      job_type,
      salary_range,
      industry,
      min_gpa,
      required_skills: skills,
      description,
      requirements
    });
    showToast('Đăng tin tuyển dụng thành công!', 'success');
    navigateTab('recruiter-jobs');
  } catch (err) {
    showToast('Lỗi đăng tin: ' + err.message, 'error');
  }
}

async function viewJobApplicationsModal(jobId) {
  try {
    const apps = await API.getJobApplications(jobId);
    const modal = document.getElementById('main-modal');
    const modalContent = document.getElementById('modal-content');

    modalContent.innerHTML = `
      <div class="p-6 max-h-[85vh] overflow-y-auto">
        <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
          <div>
            <h3 class="font-extrabold text-slate-900 text-lg">Danh sách Ứng viên Nộp đơn (${apps.length})</h3>
            <p class="text-xs text-slate-500">Được sắp xếp theo điểm tương thích trí tuệ nhân tạo (AI Match Score)</p>
          </div>
          <button onclick="closeModal()" class="p-2 text-slate-400 hover:text-slate-600 rounded-lg">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>

        <div class="space-y-4">
          ${apps.length ? apps.map(app => `
            <div class="bg-slate-50 p-4 rounded-2xl border border-slate-200 space-y-3">
              <div class="flex items-start justify-between">
                <div>
                  <h4 class="font-bold text-slate-900 text-sm">${app.student?.full_name}</h4>
                  <p class="text-xs text-slate-500">${app.student?.university} • ${app.student?.major} (GPA ${app.student_profile?.gpa}/4.0)</p>
                  <p class="text-xs text-slate-500">Email: ${app.student?.email} • SĐT: ${app.student?.phone}</p>
                </div>

                <div class="text-right">
                  <div class="text-xs font-bold px-3 py-1 rounded-full bg-blue-100 text-blue-800 inline-block mb-1">
                    🤖 Khớp: ${app.match_score}%
                  </div>
                </div>
              </div>

              ${app.cover_note ? `
                <div class="bg-white p-2.5 rounded-xl border border-slate-200 text-xs text-slate-700 italic">
                  "${app.cover_note}"
                </div>
              ` : ''}

              <div class="flex items-center justify-between pt-2 border-t border-slate-200/60">
                <div class="text-xs">
                  <span class="text-slate-400">Trạng thái:</span>
                  <select onchange="updateAppStatus('${app.id}', this.value)" class="ml-1 text-xs bg-white border border-slate-300 rounded-lg px-2 py-1 font-semibold">
                    <option value="applied" ${app.status === 'applied' ? 'selected' : ''}>Đã nộp</option>
                    <option value="reviewing" ${app.status === 'reviewing' ? 'selected' : ''}>Đang xem xét</option>
                    <option value="interview_scheduled" ${app.status === 'interview_scheduled' ? 'selected' : ''}>Mời phỏng vấn</option>
                    <option value="accepted" ${app.status === 'accepted' ? 'selected' : ''}>Trúng tuyển (Accept)</option>
                    <option value="rejected" ${app.status === 'rejected' ? 'selected' : ''}>Từ chối</option>
                  </select>
                </div>
              </div>
            </div>
          `).join('') : `
            <div class="text-center py-10 text-slate-400 text-xs">
              Chưa có ứng viên nào nộp đơn vị trí này.
            </div>
          `}
        </div>
      </div>
    `;

    modal.classList.remove('hidden');
  } catch (err) {
    showToast('Lỗi xem ứng viên: ' + err.message, 'error');
  }
}

async function updateAppStatus(appId, newStatus) {
  try {
    await API.updateApplicationStatus(appId, newStatus);
    showToast('Đã cập nhật trạng thái ứng viên!', 'success');
  } catch (err) {
    showToast('Lỗi cập nhật: ' + err.message, 'error');
  }
}

async function viewAiMatchedCandidatesModal(jobId) {
  try {
    const list = await API.getMatchedCandidates(jobId);
    const modal = document.getElementById('main-modal');
    const modalContent = document.getElementById('modal-content');

    modalContent.innerHTML = `
      <div class="p-6 max-h-[85vh] overflow-y-auto">
        <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
          <div>
            <span class="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">AI Proactive Sourcing</span>
            <h3 class="font-extrabold text-slate-900 text-lg mt-1">Ứng viên Tiềm năng Toàn Trường</h3>
            <p class="text-xs text-slate-500">AI tự động quét cơ sở dữ liệu sinh viên và gợi ý người có năng lực tiệm cận nhất với JD.</p>
          </div>
          <button onclick="closeModal()" class="p-2 text-slate-400 hover:text-slate-600 rounded-lg">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>

        <div class="space-y-4">
          ${list.map(item => `
            <div class="bg-slate-50 p-4 rounded-2xl border border-slate-200 space-y-2">
              <div class="flex items-start justify-between">
                <div>
                  <h4 class="font-bold text-slate-900 text-sm">${item.student.full_name}</h4>
                  <p class="text-xs text-slate-500">${item.student.university} • ${item.student.major} (GPA ${item.student.gpa}/4.0)</p>
                  <p class="text-xs text-slate-500">Email: ${item.student.email} • Tốt nghiệp: ${item.student.graduation_year}</p>
                </div>

                <div class="text-right">
                  <div class="text-xs font-bold px-3 py-1 rounded-full ${item.match_score >= 80 ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'}">
                    🤖 Khớp: ${item.match_score}%
                  </div>
                </div>
              </div>

              <div class="text-xs text-slate-600 space-y-1 bg-white p-2.5 rounded-xl border border-slate-100">
                <div><strong class="text-emerald-700">Điểm mạnh:</strong> ${(item.strengths || []).join(', ')}</div>
                <div><strong class="text-slate-500">Kỹ năng:</strong> ${(item.student.skills || []).join(', ')}</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    modal.classList.remove('hidden');
  } catch (err) {
    showToast('Lỗi tìm ứng viên: ' + err.message, 'error');
  }
}

function renderRecruiterCandidatesView(container) {
  renderRecruiterJobsView(container);
}

// ==========================================
// 7. ADMIN & MARKET INTELLIGENCE VIEW
// ==========================================
async function renderAdminStatsView(container) {
  let stats = {};
  try {
    stats = await API.getMarketTrends();
  } catch (e) {}

  container.innerHTML = `
    <div class="space-y-6">
      <div class="gradient-hero p-6 sm:p-8 rounded-3xl border border-blue-100">
        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700 mb-2">
          🏛️ Trung tâm Hướng nghiệp & Giám sát Tuyển dụng
        </span>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Báo cáo Xu hướng Thị trường & Hiệu quả Kết nối
        </h1>
        <p class="mt-1 text-slate-600 text-sm max-w-2xl">
          Phân tích dữ liệu thời gian thực về tỷ lệ sinh viên có việc làm sau tốt nghiệp, nhu cầu kỹ năng nóng và phân bổ mức lương.
        </p>
      </div>

      <!-- KPI Metrics -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="text-xs font-bold text-slate-400 uppercase">Tỷ lệ có việc làm</div>
          <div class="text-3xl font-black text-emerald-600 mt-1">${stats.placement_rate || 78.4}%</div>
          <div class="text-[11px] text-emerald-700 font-semibold mt-1">↑ +6.2% so với cùng kỳ</div>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="text-xs font-bold text-slate-400 uppercase">Độ khớp trung bình</div>
          <div class="text-3xl font-black text-blue-600 mt-1">${stats.avg_match_score || 82.5}%</div>
          <div class="text-[11px] text-blue-700 font-semibold mt-1">Chuẩn xác theo JD doanh nghiệp</div>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="text-xs font-bold text-slate-400 uppercase">Vị trí đang mở</div>
          <div class="text-3xl font-black text-slate-900 mt-1">${stats.active_jobs_count || 18}</div>
          <div class="text-[11px] text-slate-500 font-medium mt-1">Từ 8 doanh nghiệp đối tác</div>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="text-xs font-bold text-slate-400 uppercase">Lượt kết nối thành công</div>
          <div class="text-3xl font-black text-purple-600 mt-1">${stats.hired_count || 24}</div>
          <div class="text-[11px] text-purple-700 font-semibold mt-1">Sinh viên nhận Offer</div>
        </div>
      </div>

      <!-- Charts & Tables Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Top Skills In Demand -->
        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="font-extrabold text-slate-900 text-sm">Top 8 Kỹ năng được Doanh nghiệp Săn đón</h3>
            <span class="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded font-bold">Q4 2026</span>
          </div>

          <div class="space-y-3">
            ${(stats.top_skills || []).map((s, idx) => `
              <div class="flex items-center justify-between text-xs">
                <div class="flex items-center space-x-2 w-48">
                  <span class="font-bold text-slate-400">#${idx + 1}</span>
                  <span class="font-semibold text-slate-800">${s.skill}</span>
                </div>
                <div class="flex-1 mx-3 bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div class="bg-blue-600 h-2 rounded-full" style="width: ${Math.min(100, s.demand_count * 2)}%"></div>
                </div>
                <div class="text-right">
                  <span class="font-bold text-slate-900">${s.demand_count} bài đăng</span>
                  <span class="text-emerald-600 text-[11px] ml-1 font-semibold">${s.growth_percentage}</span>
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Salary Benchmarks -->
        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <h3 class="font-extrabold text-slate-900 text-sm">Thang Lương Thị trường theo Cấp độ</h3>

          <div class="space-y-3.5">
            ${(stats.salary_benchmarks || []).map(b => `
              <div class="bg-slate-50 p-4 rounded-xl border border-slate-200 flex items-center justify-between">
                <div>
                  <h4 class="font-bold text-slate-900 text-xs sm:text-sm">${b.level}</h4>
                  <div class="text-xs text-slate-500 mt-0.5">Tốc độ tuyển: ${b.hiring_speed}</div>
                </div>
                <div class="text-right">
                  <div class="text-sm sm:text-base font-extrabold text-emerald-700">${b.avg_salary}</div>
                  <div class="text-[11px] text-slate-400 font-medium">${b.openings} chỉ tiêu tuyển</div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    </div>
  `;
}

// 8. USER MANAGEMENT VIEW (ADMIN)
async function renderAdminUsersView(container) {
  let users = [];
  try {
    users = await API.getUsers();
  } catch (e) {}

  container.innerHTML = `
    <div class="space-y-6">
      <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 class="text-xl sm:text-2xl font-black text-slate-900">Quản lý Người dùng & Phân quyền</h2>
          <p class="text-xs sm:text-sm text-slate-500">Quản lý danh sách sinh viên, nhà tuyển dụng và cán bộ hướng nghiệp.</p>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-50 text-slate-500 font-bold border-b border-slate-200">
              <tr>
                <th class="p-4">Họ và tên</th>
                <th class="p-4">Email</th>
                <th class="p-4">Vai trò (Role)</th>
                <th class="p-4">Đơn vị / Chuyên ngành</th>
                <th class="p-4">Trạng thái</th>
                <th class="p-4 text-right">Hành động</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 text-slate-700">
              ${users.map(u => `
                <tr class="hover:bg-slate-50/50">
                  <td class="p-4 font-bold text-slate-900">${u.full_name}</td>
                  <td class="p-4 font-mono text-slate-500">${u.email}</td>
                  <td class="p-4">
                    <span class="px-2.5 py-1 rounded-md text-xs font-bold ${
                      u.role === 'admin' ? 'bg-purple-100 text-purple-800' :
                      u.role === 'recruiter' ? 'bg-blue-100 text-blue-800' :
                      'bg-emerald-100 text-emerald-800'
                    }">
                      ${getRoleBadge(u.role)}
                    </span>
                  </td>
                  <td class="p-4">${u.university} - ${u.major}</td>
                  <td class="p-4">
                    <span class="px-2 py-0.5 rounded text-xs font-semibold ${u.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'}">
                      ${u.is_active ? 'Đang hoạt động' : 'Đã khóa'}
                    </span>
                  </td>
                  <td class="p-4 text-right space-x-2">
                    <button onclick="toggleUserStatus('${u.id}', ${!u.is_active})" class="px-2.5 py-1 rounded border border-slate-200 hover:bg-slate-100 font-semibold">
                      ${u.is_active ? 'Khóa' : 'Mở khóa'}
                    </button>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;
}

async function toggleUserStatus(userId, newActive) {
  try {
    await API.updateUser(userId, { is_active: newActive });
    showToast('Đã cập nhật trạng thái người dùng!', 'success');
    renderAdminUsersView(document.getElementById('app-content'));
  } catch (err) {
    showToast('Lỗi cập nhật: ' + err.message, 'error');
  }
}

function renderAdminJobsView(container) {
  renderRecruiterJobsView(container);
}

// Global variables for registration tags
let tempRegSkills = ['Python', 'SQL', 'Git'];
let tempRegRoles = ['Backend Developer'];

function toggleSkillChip(skillName) {
  const idx = tempRegSkills.indexOf(skillName);
  if (idx > -1) {
    tempRegSkills.splice(idx, 1);
  } else {
    tempRegSkills.push(skillName);
  }
  updateSkillChipsUI();
}

function updateSkillChipsUI() {
  const container = document.getElementById('skill-chips-container');
  if (!container) return;
  const allSkills = [
    'Python', 'FastAPI', 'React.js', 'SQL', 'PostgreSQL',
    'Machine Learning', 'Deep Learning', 'PyTorch', 'Docker', 'Git',
    'Data Analysis', 'Power BI', 'JavaScript', 'TypeScript', 'Figma',
    'Google Ads', 'Meta Ads', 'SEO/SEM', 'Financial Modeling', 'Corporate Finance',
    'MISA/FAST', 'Hạch toán Kế toán', 'Tuyển dụng & C&B', 'Luật Lao động',
    'Incoterms 2020', 'Quản lý Kho bãi', 'Lập trình PLC', 'SCADA & HMI',
    'Cybersecurity', 'Excel Advanced'
  ];

  container.innerHTML = allSkills.map(s => {
    const isSelected = tempRegSkills.includes(s);
    return `
      <button type="button" onclick="toggleSkillChip('${s}')" class="px-2.5 py-1 rounded-lg text-xs font-semibold transition border ${
        isSelected
          ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
          : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-200'
      }">
        ${isSelected ? '✓ ' : '+ '}${s}
      </button>
    `;
  }).join('');
}

function toggleRoleChip(roleName) {
  const idx = tempRegRoles.indexOf(roleName);
  if (idx > -1) {
    tempRegRoles.splice(idx, 1);
  } else {
    tempRegRoles.push(roleName);
  }
  updateRoleChipsUI();
}

function updateRoleChipsUI() {
  const container = document.getElementById('role-chips-container');
  if (!container) return;
  const allRoles = [
    'Backend Developer', 'Frontend Developer', 'AI / Machine Learning Engineer',
    'Data Analyst / Business Intelligence', 'DevOps / Cloud Engineer', 'Product Manager / Business Analyst (BA)',
    'Digital Marketing & Performance Media', 'Financial Analyst & Phân tích Tài chính',
    'Kế toán & Kiểm toán (Auditing & Accounting)', 'HR & Quản trị Nhân sự (Talent Acquisition)',
    'Supply Chain & Quản trị Chuỗi Cung ứng (Logistics)', 'UI/UX & Product Designer',
    'Kỹ sư Tự động hóa & Cơ điện tử (Automation & Robotics)'
  ];

  container.innerHTML = allRoles.map(r => {
    const isSelected = tempRegRoles.includes(r);
    return `
      <button type="button" onclick="toggleRoleChip('${r}')" class="px-2.5 py-1 rounded-lg text-xs font-semibold transition border ${
        isSelected
          ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
          : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-200'
      }">
        ${isSelected ? '★ ' : ''}${r}
      </button>
    `;
  }).join('');
}

// Enhanced Auth Modal
async function openAuthModal(defaultMode = 'register-student') {
  const modal = document.getElementById('main-modal');
  const modalContent = document.getElementById('modal-content');
  if (!modal || !modalContent) return;

  let registeredStudents = [];
  try {
    registeredStudents = await API.getRegisteredStudents();
  } catch (e) {
    registeredStudents = [];
  }

  modalContent.innerHTML = `
    <div class="p-6 sm:p-8 max-h-[90vh] overflow-y-auto">
      <!-- Modal Header -->
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <div>
          <span class="text-xs font-bold text-blue-600 bg-blue-50 px-2.5 py-0.5 rounded-full uppercase tracking-wider">Hệ thống CareerBridge AI</span>
          <h3 class="text-xl font-black text-slate-900 mt-1" id="auth-modal-title">
            ${defaultMode === 'register-student' ? '🎓 Đăng ký Tài khoản Sinh viên Mới' : defaultMode === 'login' ? '🔑 Đăng nhập Hệ thống' : '🏢 Đăng ký Doanh nghiệp'}
          </h3>
        </div>
        <button onclick="closeModal()" class="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex border-b border-slate-200 mb-5 text-xs sm:text-sm font-semibold">
        <button type="button" onclick="openAuthModal('register-student')" class="py-2.5 px-4 transition ${defaultMode === 'register-student' ? 'text-blue-600 border-b-2 border-blue-600 font-bold' : 'text-slate-500 hover:text-slate-800'}">
          🎓 Đăng ký Sinh viên Mới
        </button>
        <button type="button" onclick="openAuthModal('login')" class="py-2.5 px-4 transition ${defaultMode === 'login' ? 'text-blue-600 border-b-2 border-blue-600 font-bold' : 'text-slate-500 hover:text-slate-800'}">
          🔑 Đăng nhập
        </button>
        <button type="button" onclick="openAuthModal('register-recruiter')" class="py-2.5 px-4 transition ${defaultMode === 'register-recruiter' ? 'text-blue-600 border-b-2 border-blue-600 font-bold' : 'text-slate-500 hover:text-slate-800'}">
          🏢 Dành cho Doanh nghiệp
        </button>
      </div>

      <!-- Content Views -->
      ${defaultMode === 'register-student' ? `
        <!-- Student Registration Form -->
        <div class="space-y-4">
          <div class="bg-blue-50 p-3 rounded-xl border border-blue-100 text-xs text-blue-800 flex items-center space-x-2">
            <span class="text-base">✨</span>
            <span>Sau khi đăng ký, AI sẽ tự động phân tích hồ sơ và tính điểm phù hợp với các cơ hội việc làm thực tế!</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Họ và tên sinh viên: <span class="text-rose-500">*</span></label>
              <input type="text" id="reg-name" placeholder="VD: Trần Gia Hân"
                class="w-full text-xs sm:text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:bg-white">
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Email sinh viên: <span class="text-rose-500">*</span></label>
              <input type="email" id="reg-email" placeholder="VD: giahan.tran@gmail.com"
                class="w-full text-xs sm:text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:bg-white">
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Mật khẩu (tối thiểu 6 ký tự): <span class="text-rose-500">*</span></label>
              <input type="password" id="reg-password" placeholder="••••••••"
                class="w-full text-xs sm:text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:bg-white">
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Số điện thoại:</label>
              <input type="tel" id="reg-phone" placeholder="VD: 0912345678"
                class="w-full text-xs sm:text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:bg-white">
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Trường Đại học:</label>
              <select id="reg-uni" class="w-full text-xs sm:text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500">
                <option value="Đại học Bách Khoa">Đại học Bách Khoa (HCMUT / HUST)</option>
                <option value="Đại học Khoa học Tự nhiên">Đại học Khoa học Tự nhiên (HCMUS / HUS)</option>
                <option value="Đại học Công nghệ Thông tin">Đại học Công nghệ Thông tin (UIT)</option>
                <option value="Đại học Quốc gia">Đại học Quốc gia</option>
                <option value="Đại học Kinh tế Quốc dân">Đại học Kinh tế Quốc dân (NEU)</option>
                <option value="Đại học Ngoại thương">Đại học Ngoại thương (FTU)</option>
                <option value="Đại học FPT">Đại học FPT</option>
                <option value="Học viện Công nghệ Bưu chính Viễn thông">Học viện Bưu chính Viễn thông (PTIT)</option>
                <option value="Đại học Sư phạm Kỹ thuật">Đại học Sư phạm Kỹ thuật (HCMUTE)</option>
                <option value="Trường Đại học khác">Trường Đại học khác</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Chuyên ngành đào tạo:</label>
              <select id="reg-major" class="w-full text-xs sm:text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500">
                <option value="Khoa học Máy tính & Kỹ thuật Phần mềm">Khoa học Máy tính & Kỹ thuật Phần mềm</option>
                <option value="Trí tuệ Nhân tạo & Khoa học Dữ liệu">Trí tuệ Nhân tạo & Khoa học Dữ liệu</option>
                <option value="Công nghệ Thông tin">Công nghệ Thông tin</option>
                <option value="Hệ thống Thông tin Quản lý">Hệ thống Thông tin Quản lý (MIS)</option>
                <option value="An toàn Thông tin / Mạng máy tính">An toàn Thông tin & Mạng máy tính</option>
                <option value="Digital Marketing & Thương mại điện tử">Digital Marketing & E-commerce</option>
                <option value="Tài chính - Ngân hàng & Chứng khoán">Tài chính - Ngân hàng & Chứng khoán</option>
                <option value="Kế toán - Kiểm toán">Kế toán - Kiểm toán</option>
                <option value="Logistics & Quản trị Chuỗi cung ứng">Logistics & Quản trị Chuỗi cung ứng</option>
                <option value="Quản trị Nhân sự & Tổ chức">Quản trị Nhân sự & Tổ chức (HRM)</option>
                <option value="Thiết kế Đồ họa & UI/UX">Thiết kế Đồ họa & UI/UX</option>
                <option value="Kỹ thuật Cơ điện tử & Tự động hóa">Kỹ thuật Cơ điện tử & Tự động hóa</option>
                <option value="Quản trị Kinh doanh & Phân tích Nghiệp vụ">Quản trị Kinh doanh & BA</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Khóa / Năm tốt nghiệp:</label>
              <select id="reg-grad-year" class="w-full text-xs sm:text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl">
                <option value="2025">2025 (Chuẩn bị tốt nghiệp)</option>
                <option value="2026" selected>2026 (Năm cuối)</option>
                <option value="2027">2027 (Năm 3)</option>
                <option value="2028">2028 (Năm 2)</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Điểm GPA tích lũy (hệ 4.0):</label>
              <input type="number" step="0.05" id="reg-gpa" value="3.4"
                class="w-full text-xs sm:text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl">
            </div>
          </div>

          <!-- Selectable Skill Chips -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1.5">
              Chọn các kỹ năng bạn có (Bấm để chọn/bỏ chọn):
            </label>
            <div id="skill-chips-container" class="flex flex-wrap gap-1.5 p-3 bg-slate-50 rounded-xl border border-slate-200">
            </div>
          </div>

          <!-- Selectable Dream Roles -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1.5">
              Vị trí mong muốn ứng tuyển:
            </label>
            <div id="role-chips-container" class="flex flex-wrap gap-1.5 p-3 bg-slate-50 rounded-xl border border-slate-200">
            </div>
          </div>

          <button type="button" onclick="submitStudentRegister()" id="btn-submit-student-reg"
            class="w-full py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold text-sm rounded-xl shadow-lg shadow-blue-500/20 transition flex items-center justify-center space-x-2">
            <span>🚀 Tạo Tài Khoản Sinh Viên & Bắt Đầu Ghép Nối AI</span>
          </button>
        </div>
      ` : defaultMode === 'login' ? `
        <!-- Login Form -->
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Email đăng nhập:</label>
            <input type="email" id="auth-email" placeholder="example@gmail.com hoặc email trường"
              class="w-full text-xs sm:text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500">
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Mật khẩu:</label>
            <input type="password" id="auth-password" placeholder="••••••••"
              class="w-full text-xs sm:text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500">
          </div>

          <button type="button" onclick="submitLogin()"
            class="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-xl shadow-md transition">
            Đăng nhập ngay
          </button>

          <!-- Quick Login Accounts List -->
          <div class="pt-4 border-t border-slate-200">
            <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Hoặc bấm 1-click để đăng nhập vào tài khoản có sẵn:
            </h4>

            <div class="space-y-1.5 max-h-48 overflow-y-auto">
              ${registeredStudents.map(s => `
                <div onclick="quickLoginStudent('${s.email}')"
                  class="p-2.5 rounded-xl border border-slate-200 hover:border-blue-400 bg-slate-50 hover:bg-blue-50 transition cursor-pointer flex items-center justify-between text-xs">
                  <div>
                    <div class="font-bold text-slate-800">🎓 ${s.full_name}</div>
                    <div class="text-[11px] text-slate-500">${s.major} • GPA ${s.gpa} • ${(s.skills || []).slice(0, 3).join(', ')}</div>
                  </div>
                  <span class="text-blue-600 font-bold text-xs bg-white px-2 py-1 rounded-md border border-blue-200">Đăng nhập →</span>
                </div>
              `).join('')}

              <div onclick="switchRole('recruiter'); closeModal();"
                class="p-2.5 rounded-xl border border-slate-200 hover:border-blue-400 bg-slate-50 hover:bg-blue-50 transition cursor-pointer flex items-center justify-between text-xs">
                <div>
                  <div class="font-bold text-slate-800">🏢 FPT Software Recruiter</div>
                  <div class="text-[11px] text-slate-500">Nhà tuyển dụng doanh nghiệp</div>
                </div>
                <span class="text-blue-600 font-bold text-xs bg-white px-2 py-1 rounded-md border border-blue-200">Đăng nhập →</span>
              </div>

              <div onclick="switchRole('admin'); closeModal();"
                class="p-2.5 rounded-xl border border-slate-200 hover:border-blue-400 bg-slate-50 hover:bg-blue-50 transition cursor-pointer flex items-center justify-between text-xs">
                <div>
                  <div class="font-bold text-slate-800">🏛️ Trung tâm Hướng nghiệp (Admin)</div>
                  <div class="text-[11px] text-slate-500">Ban giám hiệu & quản trị viên</div>
                </div>
                <span class="text-blue-600 font-bold text-xs bg-white px-2 py-1 rounded-md border border-blue-200">Đăng nhập →</span>
              </div>
            </div>
          </div>
        </div>
      ` : `
        <!-- Recruiter Register Form -->
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Họ tên người phụ trách tuyển dụng:</label>
            <input type="text" id="rec-name" placeholder="VD: Lê Mai Anh" class="w-full text-xs sm:text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl">
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Tên Doanh nghiệp / Công ty:</label>
            <input type="text" id="rec-company" placeholder="VD: Tập đoàn Công nghệ VNG" class="w-full text-xs sm:text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl">
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Email doanh nghiệp:</label>
            <input type="email" id="rec-email" placeholder="recruitment@company.com" class="w-full text-xs sm:text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl">
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">Mật khẩu:</label>
            <input type="password" id="rec-password" placeholder="••••••••" class="w-full text-xs sm:text-sm p-3 bg-slate-50 border border-slate-200 rounded-xl">
          </div>
          <button type="button" onclick="submitRecruiterRegister()" class="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-xl shadow-md transition">
            Đăng ký Tài khoản Doanh nghiệp
          </button>
        </div>
      `}
    </div>
  `;

  modal.classList.remove('hidden');

  if (defaultMode === 'register-student') {
    updateSkillChipsUI();
    updateRoleChipsUI();
  }
}

async function quickLoginStudent(email) {
  try {
    const res = await API.login(email, 'password123');
    currentUser = res.user;
    closeModal();
    showToast(`Đã đăng nhập thành công vào tài khoản: ${currentUser.full_name}!`, 'success');
    activeTab = 'jobs';
    updateNavbar();
    navigateTab('jobs');
  } catch (e) {
    showToast('Lỗi đăng nhập: ' + e.message, 'error');
  }
}

async function submitStudentRegister() {
  const full_name = document.getElementById('reg-name')?.value.trim();
  const email = document.getElementById('reg-email')?.value.trim();
  const password = document.getElementById('reg-password')?.value;
  const phone = document.getElementById('reg-phone')?.value.trim() || '';
  const university = document.getElementById('reg-uni')?.value || 'Đại học Bách Khoa';
  const major = document.getElementById('reg-major')?.value || 'Công nghệ Thông tin';
  const graduation_year = parseInt(document.getElementById('reg-grad-year')?.value || '2026');
  const gpa = parseFloat(document.getElementById('reg-gpa')?.value || '3.4');

  if (!full_name) {
    showToast('Vui lòng nhập họ và tên sinh viên', 'warning');
    return;
  }
  if (!email || !email.includes('@')) {
    showToast('Vui lòng nhập địa chỉ email hợp lệ', 'warning');
    return;
  }
  if (!password || password.length < 6) {
    showToast('Mật khẩu cần tối thiểu 6 ký tự', 'warning');
    return;
  }

  const btn = document.getElementById('btn-submit-student-reg');
  if (btn) btn.disabled = true;

  try {
    const payload = {
      full_name,
      email,
      password,
      role: 'student',
      phone,
      university,
      major,
      graduation_year,
      gpa,
      skills: tempRegSkills,
      dream_roles: tempRegRoles
    };

    const res = await API.register(payload);
    currentUser = res.user;
    closeModal();
    showToast(`🎉 Chúc mừng bạn ${currentUser.full_name} đã đăng ký tài khoản thành công!`, 'success');
    activeTab = 'jobs';
    updateNavbar();
    navigateTab('jobs');
  } catch (err) {
    showToast('Đăng ký thất bại: ' + err.message, 'error');
  } finally {
    if (btn) btn.disabled = false;
  }
}

async function submitRecruiterRegister() {
  const full_name = document.getElementById('rec-name')?.value.trim();
  const company = document.getElementById('rec-company')?.value.trim();
  const email = document.getElementById('rec-email')?.value.trim();
  const password = document.getElementById('rec-password')?.value;

  if (!full_name || !email || !password) {
    showToast('Vui lòng điền đủ thông tin', 'warning');
    return;
  }

  try {
    const res = await API.register({
      full_name: `${full_name} (${company || 'Doanh nghiệp'})`,
      email,
      password,
      role: 'recruiter',
      university: company || 'Doanh nghiệp đối tác'
    });
    currentUser = res.user;
    closeModal();
    showToast(`Đăng ký tài khoản Doanh nghiệp thành công!`, 'success');
    activeTab = 'recruiter-jobs';
    updateNavbar();
    navigateTab('recruiter-jobs');
  } catch (err) {
    showToast('Lỗi đăng ký: ' + err.message, 'error');
  }
}

async function submitLogin() {
  const email = document.getElementById('auth-email')?.value.trim();
  const password = document.getElementById('auth-password')?.value;

  if (!email || !password) {
    showToast('Vui lòng nhập email và mật khẩu', 'warning');
    return;
  }

  try {
    const res = await API.login(email, password);
    currentUser = res.user;
    closeModal();
    showToast(`Đăng nhập thành công! Chào mừng ${currentUser.full_name}`, 'success');
    activeTab = currentUser.role === 'student' ? 'jobs' : currentUser.role === 'recruiter' ? 'recruiter-jobs' : 'admin-stats';
    updateNavbar();
    navigateTab(activeTab);
  } catch (err) {
    showToast('Đăng nhập thất bại: ' + err.message, 'error');
  }
}

// Global exposure
window.switchRole = switchRole;
window.navigateTab = navigateTab;
window.openJobDetailModal = openJobDetailModal;
window.submitApplication = submitApplication;
window.closeModal = closeModal;
window.loadSampleCV = loadSampleCV;
window.analyzeCV = analyzeCV;
window.startMockSession = startMockSession;
window.toggleVoiceRecording = toggleVoiceRecording;
window.sampleAnswerFill = sampleAnswerFill;
window.submitMockQuestionAnswer = submitMockQuestionAnswer;
window.nextMockQuestion = nextMockQuestion;
window.generateRoadmap = generateRoadmap;
window.saveStudentProfile = saveStudentProfile;
window.submitNewJob = submitNewJob;
window.viewJobApplicationsModal = viewJobApplicationsModal;
window.viewAiMatchedCandidatesModal = viewAiMatchedCandidatesModal;
window.toggleSkillChip = toggleSkillChip;
window.toggleRoleChip = toggleRoleChip;
window.submitStudentRegister = submitStudentRegister;
window.submitRecruiterRegister = submitRecruiterRegister;
window.quickLoginStudent = quickLoginStudent;
window.openAuthModal = openAuthModal;
window.submitLogin = submitLogin;
window.logout = logout;

// Bootstrap on DOM ready
document.addEventListener('DOMContentLoaded', initApp);
