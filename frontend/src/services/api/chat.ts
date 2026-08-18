import apiClient from '@/lib/api/client';
import {
  ChatContact,
  ChatGroup,
  FriendRequest,
  ChatMessage,
  UserBasic,
} from '@/types/chat';

// ========== 联系人列表 API ==========

/**
 * 获取关注列表
 */
export const getFollowingList = async (): Promise<{ count: number; results: ChatContact[] }> => {
  console.log('🔍 [API] Fetching following list...');
  const result: { count: number; results: ChatContact[] } = await apiClient.get('/chat/following/');
  console.log('✓ [API] Following list loaded:', result);
  return result;
};

/**
 * 获取粉丝列表
 */
export const getFollowersList = async (): Promise<{ count: number; results: ChatContact[] }> => {
  console.log('🔍 [API] Fetching followers list...');
  const result: { count: number; results: ChatContact[] } = await apiClient.get('/chat/followers/');
  console.log('✓ [API] Followers list loaded:', result);
  return result;
};

/**
 * 获取好友列表
 */
export const getFriendsList = async (): Promise<{ count: number; results: ChatContact[] }> => {
  console.log('🔍 [API] Fetching friends list...');
  const result: { count: number; results: ChatContact[] } = await apiClient.get('/chat/friends/');
  console.log('✓ [API] Friends list loaded:', result);
  return result;
};

/**
 * 获取群聊列表
 */
export const getGroupsList = async (): Promise<{ count: number; results: ChatGroup[] }> => {
  return await apiClient.get('/chat/groups/');
};

/**
 * 获取好友申请列表
 */
export const getFriendRequests = async (): Promise<{ count: number; results: FriendRequest[] }> => {
  return await apiClient.get('/chat/friend-requests/');
};

// ========== 消息 API ==========

/**
 * 获取聊天记录
 * @param userId - 对方用户ID（私聊时使用）
 * @param groupId - 群组ID（群聊时使用）
 */
export const getMessages = async (
  userId?: number,
  groupId?: number
): Promise<{ count: number; results: ChatMessage[] }> => {
  const params: any = {};
  if (userId) params.user_id = userId;
  if (groupId) params.group_id = groupId;

  return await apiClient.get('/chat/messages/', { params });
};

/**
 * 发送消息
 * @param data - 消息数据
 */
export const sendMessage = async (data: {
  to_user_id?: number;
  group_id?: number;
  content: string;
  message_type?: 'text' | 'image' | 'file' | 'emoji';
}): Promise<ChatMessage> => {
  return await apiClient.post('/chat/messages/send/', data);
};

/**
 * 标记消息为已读
 * @param userId - 对方用户ID（私聊时使用）
 * @param groupId - 群组ID（群聊时使用）
 */
export const markAsRead = async (
  userId?: number,
  groupId?: number
): Promise<{ marked_count: number }> => {
  const data: any = {};
  if (userId) data.user_id = userId;
  if (groupId) data.group_id = groupId;

  return await apiClient.post('/chat/messages/mark-read/', data);
};

/**
 * 获取未读消息总数
 */
export const getUnreadCount = async (): Promise<{ total_unread: number }> => {
  console.log('🔍 [API] Fetching unread count...');
  const result: { total_unread: number } = await apiClient.get('/chat/unread-count/');
  console.log('✓ [API] Unread count loaded:', result);
  return result;
};

// ========== 好友关系 API ==========

/**
 * 关注用户
 * @param userId - 用户ID
 */
export const followUser = async (
  userId: number
): Promise<{ action: string; user_id: number }> => {
  return await apiClient.post('/follow/', { user_id: userId });
};

/**
 * 取消关注
 * @param userId - 用户ID
 */
export const unfollowUser = async (userId: number): Promise<void> => {
  await apiClient.delete(`/follow/${userId}/`);
};

/**
 * 发送好友申请
 * @param userId - 用户ID
 */
export const sendFriendRequest = async (
  userId: number
): Promise<FriendRequest> => {
  return await apiClient.post('/chat/friend-request/', { to_user_id: userId });
};

/**
 * 接受好友申请
 * @param requestId - 申请ID
 */
export const acceptFriendRequest = async (
  requestId: number
): Promise<FriendRequest> => {
  return await apiClient.post(`/chat/friend-request/${requestId}/accept/`);
};

/**
 * 拒绝好友申请
 * @param requestId - 申请ID
 */
export const rejectFriendRequest = async (
  requestId: number
): Promise<FriendRequest> => {
  return await apiClient.post(`/chat/friend-request/${requestId}/reject/`);
};

// ========== 搜索 API ==========

/**
 * 搜索用户
 * @param query - 搜索关键词
 * @param type - 搜索范围（following/followers/friends/all）
 */
export const searchUsers = async (
  query: string,
  type: 'following' | 'followers' | 'friends' | 'all' = 'all'
): Promise<{ count: number; results: UserBasic[] }> => {
  return await apiClient.get('/chat/search/', {
    params: { q: query, type },
  });
};
