import { apiClient } from '@/lib/api/client';
import type {
  NotificationListResponse,
  UnreadCountResponse,
  NotificationType,
} from '@/types/notification';

export const notificationsApi = {
  /**
   * 获取通知列表
   * @param type 通知类型筛选
   * @param isRead 是否已读筛选
   * @param page 页码
   */
  getNotifications: async (params?: {
    type?: NotificationType;
    is_read?: boolean;
    page?: number;
  }): Promise<NotificationListResponse> => {
    try {
      console.log('📤 [API] getNotifications - 发送请求, params:', params);
      const response = await apiClient.get<NotificationListResponse>('/notifications/', { params });
      console.log('📥 [API] getNotifications - 原始响应:', response);
      console.log('📥 [API] getNotifications - 响应类型:', typeof response);
      console.log('📥 [API] getNotifications - 是否为数组:', Array.isArray(response));
      console.log('📥 [API] getNotifications - response.results:', response?.results);
      console.log('📥 [API] getNotifications - response.data:', response?.data);

      // apiClient已经通过resolveResponseData处理过响应，直接使用
      console.log('📥 [API] getNotifications - 准备返回:', response);
      return response as NotificationListResponse;
    } catch (error) {
      console.error('❌ [API] 获取通知列表失败:', error);
      throw error;
    }
  },

  /**
   * 获取未读通知数（包含按类型统计）
   */
  getUnreadCount: async (): Promise<UnreadCountResponse> => {
    try {
      const response = await apiClient.get<UnreadCountResponse>('/notifications/unread_count/');
      console.log('📥 getUnreadCount - 原始响应:', response);
      // apiClient已经通过resolveResponseData处理过响应，直接使用
      return response as UnreadCountResponse;
    } catch (error) {
      console.error('❌ 获取未读数量失败 - 详细错误:', error);
      if (error instanceof Error) {
        console.error('错误消息:', error.message);
        console.error('错误堆栈:', error.stack);
      }
      throw error;
    }
  },

  /**
   * 标记单个通知为已读
   */
  markAsRead: async (id: number): Promise<void> => {
    try {
      await apiClient.post(`/notifications/${id}/mark_as_read/`);
      console.log('✅ 通知已标记为已读:', id);
    } catch (error) {
      console.error('❌ 标记已读失败:', error);
      throw error;
    }
  },

  /**
   * 标记所有通知为已读
   * @param type 可选，只标记特定类型的通知
   */
  markAllAsRead: async (type?: NotificationType): Promise<{ marked_count: number }> => {
    try {
      const data = type ? { type } : {};
      const response = await apiClient.post<{ marked_count: number }>(
        '/notifications/mark_all_as_read/',
        data
      );
      console.log('✅ 批量标记已读响应:', response);
      // apiClient已经通过resolveResponseData处理过响应，直接使用
      return response as { marked_count: number };
    } catch (error) {
      console.error('❌ 批量标记已读失败:', error);
      throw error;
    }
  },

  /**
   * 清空所有通知
   */
  clearAll: async (): Promise<{ deleted_count: number }> => {
    try {
      const response = await apiClient.delete<{ deleted_count: number }>(
        '/notifications/clear_all/'
      );
      console.log('✅ 清空通知响应:', response);
      // apiClient已经通过resolveResponseData处理过响应，直接使用
      return response as { deleted_count: number };
    } catch (error) {
      console.error('❌ 清空通知失败:', error);
      throw error;
    }
  },
};

