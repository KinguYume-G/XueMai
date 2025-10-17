// 用户相关类型
export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: 'student' | 'teacher' | 'admin';
  phone?: string;
  location?: string;
  bio?: string;
  badges?: string[];
  joinDate?: string;
  isVerified?: boolean;
  isOnline?: boolean;
  lastSeen?: string;
}

export interface UserProfile extends User {
  followersCount: number;
  followingCount: number;
  postsCount: number;
  likesCount: number;
  isFollowing?: boolean;
  isOwnProfile?: boolean;
}

// 认证相关类型
export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterData {
  name: string;
  email: string;
  phone: string;
  password: string;
  confirmPassword: string;
}

export interface AuthResponse {
  token: string;
  user: User;
  refreshToken?: string;
}

// 帖子相关类型
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
  images?: string[];
  likes: number;
  comments: number;
  shares: number;
  timestamp: string;
  isLiked: boolean;
  isBookmarked: boolean;
  isShared: boolean;
  tags?: string[];
  visibility: 'public' | 'followers' | 'private';
  editedAt?: string;
}

export interface CreatePostData {
  content: string;
  images?: File[];
  tags?: string[];
  visibility?: 'public' | 'followers' | 'private';
}

export interface PostComment {
  id: string;
  author: {
    id: string;
    name: string;
    avatar?: string;
  };
  content: string;
  timestamp: string;
  likes: number;
  isLiked: boolean;
  replies?: PostComment[];
}

// 搜索相关类型
export interface SearchResult {
  type: 'user' | 'post' | 'tag' | 'school';
  id: string;
  title: string;
  description?: string;
  avatar?: string;
  metadata?: Record<string, any>;
}

export interface SearchFilters {
  type?: 'user' | 'post' | 'tag' | 'school';
  dateRange?: 'day' | 'week' | 'month' | 'year' | 'all';
  sortBy?: 'relevance' | 'date' | 'popularity';
}

// 学校专区类型
export interface SchoolZone {
  id: string;
  name: string;
  description: string;
  logo?: string;
  isLocked: boolean;
  memberCount: number;
  recentPosts: number;
  topics: string[];
}

// 热门话题类型
export interface HotTopic {
  id: string;
  tag: string;
  postCount: number;
  trend: 'up' | 'down' | 'stable';
  category?: string;
}

// 交换项目类型
export interface ExchangeProject {
  id: string;
  name: string;
  school: string;
  country: string;
  deadline: string;
  requirements: string[];
  description: string;
  isUrgent: boolean;
  contactInfo?: string;
}

// 通知类型
export interface Notification {
  id: string;
  type: 'like' | 'comment' | 'follow' | 'mention' | 'system';
  title: string;
  message: string;
  avatar?: string;
  timestamp: string;
  isRead: boolean;
  actionUrl?: string;
  metadata?: Record<string, any>;
}

// 消息类型
export interface Message {
  id: string;
  sender: {
    id: string;
    name: string;
    avatar?: string;
  };
  content: string;
  timestamp: string;
  isRead: boolean;
  type: 'text' | 'image' | 'file';
  metadata?: Record<string, any>;
}

export interface Conversation {
  id: string;
  participants: User[];
  lastMessage?: Message;
  unreadCount: number;
  isOnline: boolean;
}

// 设置类型
export interface UserSettings {
  theme: 'light' | 'dark' | 'auto';
  language: 'zh' | 'en';
  notifications: {
    email: boolean;
    push: boolean;
    likes: boolean;
    comments: boolean;
    follows: boolean;
    mentions: boolean;
  };
  privacy: {
    profileVisibility: 'public' | 'followers' | 'private';
    showEmail: boolean;
    showPhone: boolean;
    showOnlineStatus: boolean;
  };
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  pagination?: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, any>;
}

// 表单验证类型
export interface ValidationError {
  field: string;
  message: string;
}

export interface FormState<T = any> {
  data: T;
  errors: ValidationError[];
  isSubmitting: boolean;
  isValid: boolean;
}

// 路由类型
export interface RouteParams {
  id?: string;
  slug?: string;
}

// 组件Props类型
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface LoadingProps extends BaseComponentProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

export interface ModalProps extends BaseComponentProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
}

// 工具类型
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};
