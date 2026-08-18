import { apiClient } from '@/lib/api/client';
import type { PostApiRecord, PostCreateRequest, PaginatedResponse } from '@/types/api';

export const postsApi = {
  /**
   * 获取帖子列表（支持分页和筛选）
   */
  getPosts: async (params?: {
    page?: number;
    visibility?: string;
    search?: string;
    ordering?: string;
    author?: number;
  }): Promise<PaginatedResponse<PostApiRecord>> => {
    // apiClient 的 interceptor 会自动解包 data
    return apiClient.get<PaginatedResponse<PostApiRecord>>('/posts/', { params });
  },
  
  /**
   * 获取 Feed 流（推荐/最新/关注）
   */
  getFeed: async (params?: {
    tab?: 'hot' | 'new' | 'follow';
    page?: number;
  }): Promise<PaginatedResponse<PostApiRecord>> => {
    return apiClient.get<PaginatedResponse<PostApiRecord>>('/posts/feed/', { params });
  },

  /**
   * 获取单个帖子
   */
  getPost: async (id: number): Promise<PostApiRecord> => {
    return apiClient.get<PostApiRecord>(`/posts/${id}/`);
  },

  /**
   * 创建帖子
   */
  createPost: async (data: PostCreateRequest): Promise<PostCreateRequest> => {
    return apiClient.post<PostCreateRequest>('/posts/', data);
  },

  /**
   * 更新帖子
   */
  updatePost: async (id: number, data: Partial<PostCreateRequest>): Promise<PostCreateRequest> => {
    return apiClient.patch<PostCreateRequest>(`/posts/${id}/`, data);
  },

  /**
   * 删除帖子
   */
  deletePost: async (id: number): Promise<void> => {
    await apiClient.delete(`/posts/${id}/`);
  },

  /**
   * 点赞帖子（幂等操作）
   */
  likePost: async (id: number): Promise<{ status: string }> => {
    const response = await apiClient.post<{ status: string }>(`/posts/${id}/like/`);
    return response as { status: string };
  },

  /**
   * 取消点赞
   */
  unlikePost: async (id: number): Promise<{ status: string }> => {
    const response = await apiClient.post<{ status: string }>(`/posts/${id}/unlike/`);
    return response as { status: string };
  },

  /**
   * 收藏帖子
   */
  bookmarkPost: async (id: number): Promise<{ status: string }> => {
    const response = await apiClient.post<{ status: string }>(`/posts/${id}/bookmark/`);
    return response as { status: string };
  },

  /**
   * 取消收藏
   */
  unbookmarkPost: async (id: number): Promise<{ status: string }> => {
    const response = await apiClient.post<{ status: string }>(`/posts/${id}/unbookmark/`);
    return response as { status: string };
  },

  /**
   * 获取我的收藏
   */
  getMyBookmarks: async (): Promise<PaginatedResponse<PostApiRecord>> => {
    return apiClient.get<PaginatedResponse<PostApiRecord>>('/posts/my_bookmarks/');
  },
};
