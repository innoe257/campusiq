const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  role: string;
}

interface Student {
  id: number;
  student_id: string;
  first_name: string;
  last_name: string;
  email: string;
  program: string;
  major: string;
  gpa: number;
  risk_score: number | null;
  risk_category: string | null;
}

interface DashboardStats {
  total_students: number;
  active_students: number;
  risk_distribution: Record<string, number>;
  average_gpa: number;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: { document_id: string; similarity: number }[];
}

class ApiClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('campusiq_token', token);
    }
  }

  getToken(): string | null {
    if (this.token) return this.token;
    if (typeof window !== 'undefined') {
      return localStorage.getItem('campusiq_token');
    }
    return null;
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('campusiq_token');
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(error || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Auth
  async login(username: string, password: string): Promise<LoginResponse> {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Invalid credentials');
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  async register(userData: { username: string; email: string; password: string; full_name?: string; role?: string }): Promise<User> {
    return this.request<User>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getMe(): Promise<User> {
    return this.request<User>('/api/v1/auth/me');
  }

  // Students
  async getStudents(): Promise<Student[]> {
    return this.request<Student[]>('/api/v1/students');
  }

  async getDashboardStats(): Promise<DashboardStats> {
    return this.request<DashboardStats>('/api/v1/students/dashboard/stats');
  }

  // Chat
  async sendMessage(message: string, sessionId?: string): Promise<{ response: string; sources: any[]; session_id: string }> {
    return this.request('/api/v1/chat/message', {
      method: 'POST',
      body: JSON.stringify({ message, session_id: sessionId }),
    });
  }
}

export const api = new ApiClient();
export type { Student, DashboardStats, ChatMessage };
