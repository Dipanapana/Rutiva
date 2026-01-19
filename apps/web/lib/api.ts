import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, null, {
            headers: { Authorization: `Bearer ${refreshToken}` },
          });

          const { access_token, refresh_token } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// API functions
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),

  register: (data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    grade?: number;
  }) => api.post('/auth/register', data),

  logout: () => api.post('/auth/logout'),

  requestOtp: (email: string, purpose: string) =>
    api.post('/auth/otp/request', { email, purpose }),

  verifyOtp: (email: string, code: string, purpose: string) =>
    api.post('/auth/otp/verify', { email, code, purpose }),

  resetPassword: (email: string, code: string, new_password: string) =>
    api.post('/auth/password/reset', { email, code, new_password }),
};

export const productsApi = {
  list: (params?: {
    grade?: number;
    subject?: string;
    term?: number;
    featured?: boolean;
    search?: string;
    page?: number;
  }) => api.get('/products', { params }),

  getByGrade: (grade: number) => api.get(`/products/grade/${grade}`),

  getBySku: (sku: string) => api.get(`/products/${sku}`),

  listSubjects: () => api.get('/products/subjects'),

  listBundles: () => api.get('/products/bundles'),

  getBundleBySku: (sku: string) => api.get(`/products/bundles/${sku}`),
};

export const cartApi = {
  get: () => api.get('/cart'),

  addItem: (productId?: string, bundleId?: string) =>
    api.post('/cart/items', { product_id: productId, bundle_id: bundleId }),

  removeItem: (itemId: string) => api.delete(`/cart/items/${itemId}`),

  applyPromo: (code: string) => api.post('/cart/promo', { code }),

  checkout: (paymentProvider: string) =>
    api.post('/checkout', { payment_provider: paymentProvider }),
};

export const libraryApi = {
  list: () => api.get('/library'),

  get: (productId: string) => api.get(`/library/${productId}`),

  getDownloadUrl: (productId: string) => api.get(`/library/${productId}/download`),

  updateProgress: (productId: string, progressPercent: number) =>
    api.post(`/library/${productId}/progress`, { progress_percent: progressPercent }),
};

export const timetableApi = {
  list: () => api.get('/timetables'),

  create: (data: {
    product_id: string;
    exam_date: string;
    study_days: string[];
    hours_per_session?: number;
    preferred_time?: string;
    pace?: string;
  }) => api.post('/timetables', data),

  get: (id: string) => api.get(`/timetables/${id}`),

  update: (id: string, data: { settings?: object; is_active?: boolean }) =>
    api.patch(`/timetables/${id}`, data),

  completeSession: (
    id: string,
    sessionDate: string,
    sessionIndex: number,
    timeSpentMinutes?: number,
    notes?: string
  ) =>
    api.post(`/timetables/${id}/sessions/complete`, {
      session_date: sessionDate,
      session_index: sessionIndex,
      time_spent_minutes: timeSpentMinutes,
      notes,
    }),

  delete: (id: string) => api.delete(`/timetables/${id}`),

  exportIcal: (id: string) => api.get(`/timetables/${id}/ical`),
};

export const userApi = {
  getProfile: () => api.get('/users/me'),

  updateProfile: (data: {
    first_name?: string;
    last_name?: string;
    phone?: string;
    grade?: number;
    province?: string;
  }) => api.patch('/users/me', data),

  getStats: () => api.get('/users/me/stats'),
};
