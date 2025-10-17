import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// API配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // 从本地存储获取token
    const token = localStorage.getItem('authToken');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    // 处理401未授权错误
    if (error.response?.status === 401) {
      // 清除本地存储的认证信息
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      
      // 重定向到登录页
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

// API接口类型定义
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: {
    id: string;
    name: string;
    email: string;
    avatar?: string;
    role: string;
  };
}

export interface RegisterRequest {
  name: string;
  email: string;
  phone: string;
  password: string;
}

export interface Post {
  id: string;
  author: {
    id: string;
    name: string;
    avatar?: string;
    badge?: string;
  };
  content: string;
  image?: string;
  likes: number;
  comments: number;
  timestamp: string;
  isLiked: boolean;
  isBookmarked: boolean;
  tags?: string[];
}

export interface CreatePostRequest {
  content: string;
  images?: File[];
  tags?: string[];
}

// API方法
export const authAPI = {
  // 登录
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  // 注册
  register: async (userData: RegisterRequest): Promise<LoginResponse> => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  // 获取当前用户信息
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  // 更新用户资料
  updateProfile: async (profileData: any) => {
    const response = await api.put('/auth/profile', profileData);
    return response.data;
  },

  // 登出
  logout: async () => {
    await api.post('/auth/logout');
  },
};

export const postsAPI = {
  // 获取帖子列表
  getPosts: async (params?: {
    page?: number;
    limit?: number;
    tab?: string;
  }): Promise<{ posts: Post[]; total: number; page: number }> => {
    const response = await api.get('/posts', { params });
    return response.data;
  },

  // 创建帖子
  createPost: async (postData: CreatePostRequest): Promise<Post> => {
    const formData = new FormData();
    formData.append('content', postData.content);
    
    if (postData.images) {
      postData.images.forEach((image, index) => {
        formData.append(`images`, image);
      });
    }
    
    if (postData.tags) {
      formData.append('tags', JSON.stringify(postData.tags));
    }

    const response = await api.post('/posts', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // 点赞/取消点赞
  toggleLike: async (postId: string): Promise<{ isLiked: boolean; likes: number }> => {
    const response = await api.post(`/posts/${postId}/like`);
    return response.data;
  },

  // 收藏/取消收藏
  toggleBookmark: async (postId: string): Promise<{ isBookmarked: boolean }> => {
    const response = await api.post(`/posts/${postId}/bookmark`);
    return response.data;
  },

  // 获取帖子详情
  getPost: async (postId: string): Promise<Post> => {
    const response = await api.get(`/posts/${postId}`);
    return response.data;
  },
};

export const usersAPI = {
  // 搜索用户
  searchUsers: async (query: string): Promise<any[]> => {
    const response = await api.get('/users/search', { params: { q: query } });
    return response.data;
  },

  // 获取用户资料
  getUserProfile: async (userId: string) => {
    const response = await api.get(`/users/${userId}`);
    return response.data;
  },

  // 关注/取消关注用户
  toggleFollow: async (userId: string): Promise<{ isFollowing: boolean }> => {
    const response = await api.post(`/users/${userId}/follow`);
    return response.data;
  },
};

export const searchAPI = {
  // 全局搜索
  search: async (query: string, type?: string): Promise<any> => {
    const response = await api.get('/search', { 
      params: { q: query, type } 
    });
    return response.data;
  },

  // 获取热门搜索
  getTrendingSearches: async (): Promise<string[]> => {
    const response = await api.get('/search/trending');
    return response.data;
  },
};

// 导出axios实例，供其他需要的地方使用
export default api;
