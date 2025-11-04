import { apiClient } from '@/lib/api/client';
import type { Follow, PaginatedResponse } from '@/types/api';

export const socialApi = {
  /**
   * 关注/取消关注用户（幂等操作）
   * 第一次调用=关注，第二次调用=取消关注
   */
  toggleFollow: async (userId: number): Promise<{ action: string; status: string }> => {
    const response = await apiClient.post<{ action: string; status: string }>('/follow/', {
      user_id: userId,
    });
    return response as { action: string; status: string };
  },

  /**
   * 关注用户（便捷方法）
   */
  followUser: async (userId: number): Promise<{ action: string; status: string }> => {
    return socialApi.toggleFollow(userId);
  },

  /**
   * 取消关注（便捷方法）
   */
  unfollowUser: async (userId: number): Promise<{ action: string; status: string }> => {
    return socialApi.toggleFollow(userId);
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

