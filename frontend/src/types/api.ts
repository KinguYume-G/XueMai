// ========== 通用类型 ==========
export interface ApiError {
  code: string;
  message: string;
}

export interface Paging {
  count: number;
  next: string | null;
  previous: string | null;
  page_size?: number;
}

export interface ApiResponse<T> {
  data: T;
  error: ApiError | null;
  paging?: Paging | null;
}

export interface PaginatedResponse<T> {
  data: T[];
  paging: Paging;
  error: ApiError | null;
}

// ========== 用户相关 ==========
export interface Profile {
  id: number;
  user?: number;
  username?: string;
  email?: string;
  avatar?: string;
  user_bio?: string;
  avatar_url?: string;
  university?: number;
  university_name?: string;
  school?: number;
  school_name?: string;
  major: string;
  grade: string;
  followers_count: number;
  following_count: number;
  posts_count: number;
  github_url?: string;
  linkedin_url?: string;
  website?: string;
  bio?: string;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  avatar?: string;
  bio?: string;
  created_at?: string;
  profile?: Profile | null;
}

export interface ProfileUpdateRequest {
  university?: number;
  school?: number;
  major?: string;
  grade?: string;
  github_url?: string;
  linkedin_url?: string;
  website?: string;
  bio?: string;
}

// ========== 帖子相关 ==========
export type Visibility = 'public' | 'followers' | 'university' | 'private';

export interface Tag {
  id: number;
  name: string;
  slug: string;
  posts_count: number;
  created_at: string;
}

export interface Post {
  id: number;
  author: number;
  author_username: string;
  author_avatar?: string;
  title: string;
  body: string;
  image_url?: string;
  visibility: Visibility;
  is_published: boolean;
  target_university?: number;
  target_school?: number;
  tags: number[];
  tags_data: Tag[];
  likes_count: number;
  comments_count: number;
  bookmarks_count: number;
  views_count: number;
  is_liked: boolean;
  is_bookmarked: boolean;
  created_at: string;
  updated_at: string;
}

export interface PostCreateRequest {
  title?: string;
  body: string;
  image_url?: string;
  visibility?: Visibility;
  is_published?: boolean;
  target_university?: number;
  target_school?: number;
  tags?: string[];
}

// ========== 评论相关 ==========
export interface Comment {
  id: number;
  post: number;
  author: number;
  author_username: string;
  author_avatar?: string;
  content: string;
  parent?: number;
  is_reply: boolean;
  likes_count: number;
  replies_count: number;
  replies?: Comment[];
  created_at: string;
  updated_at: string;
}

export interface CommentCreateRequest {
  post: number;
  content: string;
  parent?: number;
}

// ========== 社交相关 ==========
export interface Follow {
  id: number;
  follower: number;
  following: number;
  follower_data: User;
  following_data: User;
  created_at: string;
}

// ========== 通知相关 ==========
export type NotificationType = 
  | 'post_like' 
  | 'post_comment' 
  | 'comment_reply' 
  | 'new_follower' 
  | 'mention' 
  | 'system';

export interface Notification {
  id: number;
  recipient: number;
  actor?: number;
  actor_username?: string;
  actor_avatar?: string;
  notification_type: NotificationType;
  payload: Record<string, any>;
  is_read: boolean;
  created_at: string;
}

// ========== 校园相关 ==========
export interface University {
  id: number;
  name: string;
  slug: string;
  country: string;
  city: string;
  logo?: string;
  website?: string;
  description: string;
  students_count: number;
  created_at: string;
  updated_at: string;
}

export interface School {
  id: number;
  university: number;
  university_name: string;
  name: string;
  slug: string;
  description: string;
  students_count: number;
  created_at: string;
  updated_at: string;
}

// ========== 机会相关 ==========
export interface ExchangeProgram {
  id: number;
  title: string;
  description: string;
  host_university: number;
  university: string; // 从host_university.name序列化得到的大学名称
  location: string;
  duration: string;
  deadline?: string;
  requirements: string;
  link?: string;

  // 新增字段
  country?: string;
  cover_url?: string;
  tuition?: string;
  stipend?: string;
  gpa_min?: string;
  lang_req?: string;
  website?: string;
  is_urgent?: boolean;

  // 统计字段
  rating_avg: number;
  rating_count: number;
  applied_count: number;

  // 用户相关
  bookmarked: boolean;

  // 元数据
  visibility: string;
  is_published: boolean;
  posted_by: number;
  views_count: number;
  created_at: string;
  updated_at: string;
}

export interface Internship {
  id: number;
  title: string;
  company: string;
  description: string;
  location: string;
  type: 'full_time' | 'part_time' | 'internship' | 'remote';
  duration: string;
  deadline?: string;
  requirements: string;
  salary_range: string;
  link?: string;
  visibility: string;
  is_published: boolean;
  posted_by: number;
  posted_by_username: string;
  views_count: number;
  created_at: string;
  updated_at: string;
}

