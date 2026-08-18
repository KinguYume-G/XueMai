import { apiClient } from '@/lib/api/client';
import type { Follow, PaginatedResponse } from '@/types/api';

export const socialApi = {
  /**
   * 关注用户
   * POST /follow/ (data: { user_id })
   */
  followUser: async (userId: number): Promise<{ action: string; status: string }> => {
    const response = await apiClient.post<{ action: string; status: string }>('/follow/', {
      user_id: userId,
    });
    return response as { action: string; status: string };
  },

  /**
   * 取消关注
   * DELETE /follow/{userId}/
   * Bug fix: this previously called the same POST /follow/ endpoint as
   * followUser (via a shared toggleFollow helper), so "unfollow" never
   * actually removed the Follow row — it just re-created it (a no-op
   * thanks to get_or_create on the backend). It now hits the dedicated
   * unfollow endpoint.
   */
  unfollowUser: async (userId: number): Promise<{ action: string; status: string }> => {
    await apiClient.delete(`/follow/${userId}/`);
    return { action: 'unfollowed', status: 'ok' };
  },

  /**
   * 获取我关注的人
   */
  getMyFollowing: async (): Promise<PaginatedResponse<Follow>> => {
    const response = await apiClient.get<PaginatedResponse<Follow>>('/follows/', {
      params: { type: 'following' }
    });
    return response as PaginatedResponse<Follow>;
  },

  /**
   * 获取我的粉丝
   */
  getMyFollowers: async (): Promise<PaginatedResponse<Follow>> => {
    const response = await apiClient.get<PaginatedResponse<Follow>>('/follows/', {
      params: { type: 'followers' }
    });
    return response as PaginatedResponse<Follow>;
  },
};

