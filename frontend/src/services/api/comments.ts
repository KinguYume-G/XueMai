import { apiClient } from '@/lib/api/client';
import type { Comment, CommentCreateRequest, PaginatedResponse } from '@/types/api';

export const commentsApi = {
  /**
   * 获取评论列表
   */
  getComments: async (params?: {
    post?: number;
    page?: number;
    with_replies?: boolean;
  }): Promise<PaginatedResponse<Comment>> => {
    const response = await apiClient.get<PaginatedResponse<Comment>>('/comments/', { params });
    return response as PaginatedResponse<Comment>;
  },

  /**
   * 创建评论
   */
  createComment: async (data: CommentCreateRequest): Promise<Comment> => {
    const response = await apiClient.post<Comment>('/comments/', data);
    return response as Comment;
  },

  /**
   * 删除评论
   */
  deleteComment: async (id: number): Promise<void> => {
    await apiClient.delete(`/comments/${id}/`);
  },
};

