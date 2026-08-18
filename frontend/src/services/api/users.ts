import { apiClient } from '@/lib/api/client';
import type { User, Profile, ProfileUpdateRequest } from '@/types/api';

export const usersApi = {
  /** 获取指定用户的公开/登录可见资料 */
  getUser: (id: number): Promise<User> => apiClient.get(`/users/${id}/`),

  /**
   * 获取当前用户信息
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/users/me/');
    return response as User;
  },

  /**
   * 获取当前用户资料
   */
  getCurrentProfile: async (): Promise<Profile> => {
    const response = await apiClient.get<Profile>('/profiles/me/');
    return response as Profile;
  },

  /**
   * 更新当前用户资料
   * ⚠️ 修正路径: 后端实际路径是 /auth/me/profile/
   */
  updateCurrentProfile: async (data: ProfileUpdateRequest): Promise<Profile> => {
    const response = await apiClient.put<Profile>('/auth/me/profile/', data);
    return response as Profile;
  },

  /**
   * 获取用户资料
   */
  getProfile: async (id: number): Promise<Profile> => {
    const response = await apiClient.get<Profile>(`/profiles/${id}/`);
    return response as Profile;
  },
};

