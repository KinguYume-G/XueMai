import { apiClient } from '@/lib/api/client';
import type { Notification, PaginatedResponse } from '@/types/api';

export const notificationsApi = {
  /**
   * 获取通知列表
   */
  getNotifications: async (params?: {
    page?: number;
    is_read?: boolean;
  }): Promise<PaginatedResponse<Notification>> => {
    const response = await apiClient.get<PaginatedResponse<Notification>>('/notifications/', { params });
    return response as PaginatedResponse<Notification>;
  },

  /**
   * 获取未读通知数
   */
  getUnreadCount: async (): Promise<{ unread_count: number }> => {
    const response = await apiClient.get<{ unread_count: number }>('/notifications/unread_count/');
    return response as { unread_count: number };
  },

  /**
   * 标记单个通知为已读
   */
  markAsRead: async (id: number): Promise<{ status: string }> => {
    const response = await apiClient.post<{ status: string }>(`/notifications/${id}/mark_as_read/`);
    return response as { status: string };
  },

  /**
   * 标记所有通知为已读
   */
  markAllAsRead: async (): Promise<{ status: string; count: number }> => {
    const response = await apiClient.post<{ status: string; count: number }>('/notifications/mark_all_as_read/');
    return response as { status: string; count: number };
  },

  /**
   * 清空所有已读通知
   */
  clearAll: async (): Promise<{ status: string; count: number }> => {
    const response = await apiClient.delete<{ status: string; count: number }>('/notifications/clear_all/');
    return response as { status: string; count: number };
  },
};

