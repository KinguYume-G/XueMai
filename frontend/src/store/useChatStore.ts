import { create } from 'zustand';
import {
  ChatGroup,
  UserBasic,
  ChatTab,
  ChatState,
} from '@/types/chat';
import * as chatApi from '@/services/api/chat';

interface ChatActions {
  // 弹窗控制
  setOpen: (isOpen: boolean) => void;
  setActiveTab: (tab: ChatTab) => void;

  // 数据加载
  fetchFollowingList: () => Promise<void>;
  fetchFollowersList: () => Promise<void>;
  fetchFriendsList: () => Promise<void>;
  fetchGroupsList: () => Promise<void>;
  fetchRequestsList: () => Promise<void>;
  fetchUnreadCount: () => Promise<void>;

  // 对话选择
  selectUser: (user: UserBasic) => void;
  selectGroup: (group: ChatGroup) => void;
  backToList: () => void;

  // 消息操作
  fetchMessages: (userId?: number, groupId?: number) => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  markAsRead: (userId?: number, groupId?: number) => Promise<void>;

  // 好友操作
  followUser: (userId: number) => Promise<void>;
  unfollowUser: (userId: number) => Promise<void>;
  sendFriendRequest: (userId: number) => Promise<void>;
  acceptRequest: (requestId: number) => Promise<void>;
  rejectRequest: (requestId: number) => Promise<void>;

  // 错误处理
  clearError: () => void;
}

const useChatStore = create<ChatState & ChatActions>((set, get) => ({
  // 初始状态
  isOpen: false,
  activeTab: 'friends',
  followingList: [],
  followersList: [],
  friendsList: [],
  groupsList: [],
  requestsList: [],
  selectedUser: null,
  selectedGroup: null,
  messages: [],
  unreadCount: 0,
  isLoading: false,
  error: null,

  // 弹窗控制
  setOpen: (isOpen) => {
    set({ isOpen });
    if (isOpen) {
      // 打开弹窗时，根据当前Tab加载数据
      const { activeTab } = get();
      switch (activeTab) {
        case 'following':
          get().fetchFollowingList();
          break;
        case 'followers':
          get().fetchFollowersList();
          break;
        case 'friends':
          get().fetchFriendsList();
          break;
        case 'groups':
          get().fetchGroupsList();
          break;
        case 'requests':
          get().fetchRequestsList();
          break;
      }
      // 获取未读消息数
      get().fetchUnreadCount();
    }
  },

  setActiveTab: (tab) => {
    set({ activeTab: tab });
    // 切换Tab时加载对应数据
    switch (tab) {
      case 'following':
        get().fetchFollowingList();
        break;
      case 'followers':
        get().fetchFollowersList();
        break;
      case 'friends':
        get().fetchFriendsList();
        break;
      case 'groups':
        get().fetchGroupsList();
        break;
      case 'requests':
        get().fetchRequestsList();
        break;
    }
  },

  // 数据加载
  fetchFollowingList: async () => {
    set({ isLoading: true, error: null });
    try {
      console.log('🔍 Fetching following list...');
      const data = await chatApi.getFollowingList();
      const results = Array.isArray(data?.results) ? data.results : [];
      set({ followingList: results, isLoading: false });
      console.log('✓ Following list loaded:', results.length, 'users');
    } catch (error: any) {
      console.error('❌ Failed to load following list:', error);
      set({
        error: error.message || '加载关注列表失败',
        isLoading: false,
        followingList: []
      });
    }
  },

  fetchFollowersList: async () => {
    set({ isLoading: true, error: null });
    try {
      console.log('🔍 Fetching followers list...');
      const data = await chatApi.getFollowersList();
      const results = Array.isArray(data?.results) ? data.results : [];
      set({ followersList: results, isLoading: false });
      console.log('✓ Followers list loaded:', results.length, 'users');
    } catch (error: any) {
      console.error('❌ Failed to load followers list:', error);
      set({
        error: error.message || '加载粉丝列表失败',
        isLoading: false,
        followersList: []
      });
    }
  },

  fetchFriendsList: async () => {
    set({ isLoading: true, error: null });
    try {
      console.log('🔍 Fetching friends list...');
      const data = await chatApi.getFriendsList();
      const results = Array.isArray(data?.results) ? data.results : [];
      set({ friendsList: results, isLoading: false });
      console.log('✓ Friends list loaded:', results.length, 'friends');
    } catch (error: any) {
      console.error('❌ Failed to load friends list:', error);
      set({
        error: error.message || '加载好友列表失败',
        isLoading: false,
        friendsList: []
      });
    }
  },

  fetchGroupsList: async () => {
    set({ isLoading: true, error: null });
    try {
      console.log('🔍 Fetching groups list...');
      const data = await chatApi.getGroupsList();
      const results = Array.isArray(data?.results) ? data.results : [];
      set({ groupsList: results, isLoading: false });
      console.log('✓ Groups list loaded:', results.length, 'groups');
    } catch (error: any) {
      console.error('❌ Failed to load groups list:', error);
      set({
        error: error.message || '加载群聊列表失败',
        isLoading: false,
        groupsList: []
      });
    }
  },

  fetchRequestsList: async () => {
    set({ isLoading: true, error: null });
    try {
      console.log('🔍 Fetching friend requests...');
      const data = await chatApi.getFriendRequests();
      const results = Array.isArray(data?.results) ? data.results : [];
      set({ requestsList: results, isLoading: false });
      console.log('✓ Friend requests loaded:', results.length, 'requests');
    } catch (error: any) {
      console.error('❌ Failed to load friend requests:', error);
      set({
        error: error.message || '加载好友申请失败',
        isLoading: false,
        requestsList: []
      });
    }
  },

  fetchUnreadCount: async () => {
    try {
      console.log('🔍 Fetching unread count...');
      const data = await chatApi.getUnreadCount();

      // 安全地获取 total_unread
      let unreadCount = 0;
      if (data && typeof data.total_unread === 'number') {
        unreadCount = data.total_unread;
      }

      set({ unreadCount });
      console.log('✓ Unread count loaded:', unreadCount);
    } catch (error: any) {
      console.error('❌ Failed to fetch unread count:', error);
      // 失败时设置为0，避免undefined
      set({ unreadCount: 0 });
    }
  },

  // 对话选择
  selectUser: (user) => {
    set({ selectedUser: user, selectedGroup: null });
    get().fetchMessages(user.id);
    get().markAsRead(user.id);
  },

  selectGroup: (group) => {
    set({ selectedGroup: group, selectedUser: null });
    get().fetchMessages(undefined, group.id);
    get().markAsRead(undefined, group.id);
  },

  backToList: () => {
    set({ selectedUser: null, selectedGroup: null, messages: [] });
  },

  // 消息操作
  fetchMessages: async (userId?, groupId?) => {
    set({ isLoading: true, error: null });
    try {
      console.log('🔍 Fetching messages for:', { userId, groupId });
      const data = await chatApi.getMessages(userId, groupId);
      const results = Array.isArray(data?.results) ? data.results : [];
      set({ messages: results, isLoading: false });
      console.log('✓ Messages loaded:', results.length, 'messages');
    } catch (error: any) {
      console.error('❌ Failed to load messages:', error);
      set({
        error: error.message || '加载消息失败',
        isLoading: false,
        messages: []
      });
    }
  },

  sendMessage: async (content) => {
    const { selectedUser, selectedGroup } = get();
    try {
      const data = await chatApi.sendMessage({
        to_user_id: selectedUser?.id,
        group_id: selectedGroup?.id,
        content,
        message_type: 'text',
      });

      // 添加新消息到列表
      set((state) => ({
        messages: [...state.messages, data.data],
      }));
    } catch (error: any) {
      set({ error: error.message || '发送消息失败' });
    }
  },

  markAsRead: async (userId?, groupId?) => {
    try {
      await chatApi.markAsRead(userId, groupId);
      // 更新未读消息数
      get().fetchUnreadCount();

      // 更新联系人列表中的未读数
      if (userId) {
        set((state) => ({
          followingList: state.followingList.map((c) =>
            c.user.id === userId ? { ...c, unread_count: 0 } : c
          ),
          followersList: state.followersList.map((c) =>
            c.user.id === userId ? { ...c, unread_count: 0 } : c
          ),
          friendsList: state.friendsList.map((c) =>
            c.user.id === userId ? { ...c, unread_count: 0 } : c
          ),
        }));
      }

      // 更新群组列表中的未读数
      if (groupId) {
        set((state) => ({
          groupsList: state.groupsList.map((g) =>
            g.id === groupId ? { ...g, unread_count: 0 } : g
          ),
        }));
      }
    } catch (error: any) {
      console.error('Failed to mark as read:', error);
    }
  },

  // 好友操作
  followUser: async (userId) => {
    try {
      await chatApi.followUser(userId);
      // 刷新关注列表
      get().fetchFollowingList();
    } catch (error: any) {
      set({ error: error.message || '关注失败' });
    }
  },

  unfollowUser: async (userId) => {
    try {
      await chatApi.unfollowUser(userId);
      // 刷新关注列表
      get().fetchFollowingList();
    } catch (error: any) {
      set({ error: error.message || '取消关注失败' });
    }
  },

  sendFriendRequest: async (userId) => {
    try {
      await chatApi.sendFriendRequest(userId);
      // 可以显示成功提示
    } catch (error: any) {
      set({ error: error.message || '发送好友申请失败' });
    }
  },

  acceptRequest: async (requestId) => {
    try {
      await chatApi.acceptFriendRequest(requestId);
      // 刷新好友申请列表和好友列表
      get().fetchRequestsList();
      get().fetchFriendsList();
    } catch (error: any) {
      set({ error: error.message || '接受好友申请失败' });
    }
  },

  rejectRequest: async (requestId) => {
    try {
      await chatApi.rejectFriendRequest(requestId);
      // 刷新好友申请列表
      get().fetchRequestsList();
    } catch (error: any) {
      set({ error: error.message || '拒绝好友申请失败' });
    }
  },

  // 错误处理
  clearError: () => {
    set({ error: null });
  },
}));

export default useChatStore;
