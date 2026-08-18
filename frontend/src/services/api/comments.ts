import { apiClient } from '@/lib/api/client';
import type { CommentApiRecord, CommentCreateRequest, PaginatedResponse } from '@/types/api';

export const commentsApi = {
  /**
   * 获取评论列表
   */
  getComments: async (params?: {
    post?: number;
    page?: number;
    with_replies?: boolean;
  }): Promise<PaginatedResponse<CommentApiRecord>> => {
    return apiClient.get<PaginatedResponse<CommentApiRecord>>('/comments/', { params });
  },

  /**
   * 创建评论
   */
  createComment: async (data: CommentCreateRequest): Promise<CommentCreateRequest> => {
    return apiClient.post<CommentCreateRequest>('/comments/', data);
  },

  /**
   * 删除评论
   */
  deleteComment: async (id: number): Promise<void> => {
    await apiClient.delete(`/comments/${id}/`);
  },
};
