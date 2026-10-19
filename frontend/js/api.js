// API Client for CareerBridge AI
const API = {
  baseUrl: window.location.origin,

  getToken() {
    return localStorage.getItem('cb_token');
  },

  setToken(token) {
    if (token) {
      localStorage.setItem('cb_token', token);
    } else {
      localStorage.removeItem('cb_token');
    }
  },

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (response.status === 401 && !endpoint.includes('/login')) {
        this.setToken(null);
        window.dispatchEvent(new CustomEvent('auth:expired'));
        throw new Error('Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại.');
      }

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Đã có lỗi xảy ra');
      }
      return data;
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  },

  // Auth
  async login(email, password) {
    const res = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    this.setToken(res.access_token);
    return res;
  },

  async register(data) {
    const res = await this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    this.setToken(res.access_token);
    return res;
  },

  async getMe() {
    return this.request('/api/auth/me');
  },

  async getDemoAccounts() {
    return this.request('/api/auth/demo-accounts');
  },

  async getRegisteredStudents() {
    return this.request('/api/auth/registered-students');
  },

  // Jobs
  async getJobs(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.request(`/api/jobs${qs ? `?${qs}` : ''}`);
  },

  async getJob(id) {
    return this.request(`/api/jobs/${id}`);
  },

  async createJob(data) {
    return this.request('/api/jobs', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async applyJob(jobId, coverNote = '') {
    return this.request(`/api/jobs/${jobId}/apply`, {
      method: 'POST',
      body: JSON.stringify({ job_id: jobId, cover_note: coverNote }),
    });
  },

  async getMyApplications() {
    return this.request('/api/jobs/my/applications');
  },

  async getJobApplications(jobId) {
    return this.request(`/api/jobs/${jobId}/applications`);
  },

  async updateApplicationStatus(appId, status) {
    return this.request(`/api/jobs/applications/${appId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  },

  async getMatchedCandidates(jobId) {
    return this.request(`/api/jobs/${jobId}/ai-matched-candidates`);
  },

  // Student Profile & AI Tools
  async getStudentProfile() {
    return this.request('/api/students/profile');
  },

  async updateStudentProfile(data) {
    return this.request('/api/students/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async reviewCV(cvText, targetRole = '') {
    return this.request('/api/students/cv-review', {
      method: 'POST',
      body: JSON.stringify({ cv_text: cvText, target_role: targetRole }),
    });
  },

  async getCVReviews() {
    return this.request('/api/students/cv-reviews');
  },

  async startMockInterview(roleTitle, difficulty, interviewType) {
    return this.request('/api/students/mock-interview/start', {
      method: 'POST',
      body: JSON.stringify({
        role_title: roleTitle,
        difficulty: difficulty || 'Fresher / Thực tập sinh',
        interview_type: interviewType || 'Tổng hợp (Kỹ thuật + Tình huống + Behavioral)'
      }),
    });
  },

  async submitMockAnswer(interviewId, questionIndex, userAnswer) {
    return this.request('/api/students/mock-interview/answer', {
      method: 'POST',
      body: JSON.stringify({
        interview_id: interviewId,
        question_index: questionIndex,
        user_answer: userAnswer,
      }),
    });
  },

  async getMockInterviews() {
    return this.request('/api/students/mock-interviews');
  },

  async generateRoadmap(targetRole) {
    return this.request('/api/students/roadmap', {
      method: 'POST',
      body: JSON.stringify({ target_role: targetRole }),
    });
  },

  async getRoadmaps() {
    return this.request('/api/students/roadmaps');
  },

  // Users (Admin)
  async getUsers(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.request(`/api/users${qs ? `?${qs}` : ''}`);
  },

  async updateUser(userId, data) {
    return this.request(`/api/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  // Analytics
  async getMarketTrends() {
    return this.request('/api/analytics/market-trends');
  }
};

window.API = API;
