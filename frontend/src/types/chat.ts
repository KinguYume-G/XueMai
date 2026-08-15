// 聊天系统类型定义

export interface UserBasic {
  id: number;
  username: string;
  email?: string;
  avatar?: string;
  school?: string;
  major?: string;
  is_online?: boolean;
  last_seen?: string | null;
}

export interface ChatContact {
  user: UserBasic;
  unread_count: number;
  last_message_time?: string;
  last_message?: {
    content: string;
    created_at: string;
    is_read: boolean;
    from_me: boolean;
  } | null;
  is_online: boolean;
}

export interface ChatGroup {
  id: number;
  name: string;
  description?: string;
  avatar_url?: string;
  creator: UserBasic;
  member_count: number;
  created_at: string;
  unread_count?: number;
  last_message_time?: string;
}

export interface FriendRequest {
  id: number;
  from_user: UserBasic;
  to_user: UserBasic;
  status: 'pending' | 'accepted' | 'rejected';
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: number;
  from_user: UserBasic;
  to_user?: UserBasic;
  group?: {
    id: number;
    name: string;
    avatar_url?: string;
  };
  content: string;
  message_type: 'text' | 'image' | 'file' | 'emoji';
  is_read: boolean;
  created_at: string;
}

export type ChatTab = 'following' | 'followers' | 'friends' | 'groups' | 'requests';

export interface ChatState {
  isOpen: boolean;
  activeTab: ChatTab;
  followingList: ChatContact[];
  followersList: ChatContact[];
  friendsList: ChatContact[];
  groupsList: ChatGroup[];
  requestsList: FriendRequest[];
  selectedUser: UserBasic | null;
  selectedGroup: ChatGroup | null;
  messages: ChatMessage[];
  unreadCount: number;
  isLoading: boolean;
  error: string | null;
}
