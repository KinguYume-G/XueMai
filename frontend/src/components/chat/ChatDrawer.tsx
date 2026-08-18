import React, { useState, useEffect } from 'react';
import { X, Search, Users, MessageCircle } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { ChatTab, ChatContact, ChatGroup, FriendRequest } from '@/types/chat';

interface ChatDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  activeTab: ChatTab;
  onTabChange: (tab: ChatTab) => void;
  followingList: ChatContact[];
  followersList: ChatContact[];
  friendsList: ChatContact[];
  groupsList: ChatGroup[];
  requestsList: FriendRequest[];
  onContactClick: (contact: ChatContact) => void;
  onGroupClick: (group: ChatGroup) => void;
  onAcceptRequest: (requestId: number) => void;
  onRejectRequest: (requestId: number) => void;
  isLoading: boolean;
}

const ChatDrawer: React.FC<ChatDrawerProps> = ({
  isOpen,
  onClose,
  activeTab,
  onTabChange,
  followingList,
  followersList,
  friendsList,
  groupsList,
  requestsList,
  onContactClick,
  onGroupClick,
  onAcceptRequest,
  onRejectRequest,
  isLoading,
}) => {
  const { t, i18n } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');

  // 当弹窗关闭时重置搜索
  useEffect(() => {
    if (!isOpen) {
      setSearchQuery('');
    }
  }, [isOpen]);

  if (!isOpen) return null;

  // Tab配置
  const tabs: Array<{ key: ChatTab; label: string; count: number }> = [
    { key: 'following', label: t('chat.tabs.following'), count: followingList.length },
    { key: 'followers', label: t('chat.tabs.followers'), count: followersList.length },
    { key: 'friends', label: t('chat.tabs.friends'), count: friendsList.length },
    { key: 'groups', label: t('chat.tabs.groups'), count: groupsList.length },
    { key: 'requests', label: t('chat.tabs.requests'), count: requestsList.length },
  ];

  // 获取当前Tab的数据
  const getCurrentList = () => {
    switch (activeTab) {
      case 'following':
        return followingList;
      case 'followers':
        return followersList;
      case 'friends':
        return friendsList;
      case 'groups':
        return groupsList;
      case 'requests':
        return requestsList;
      default:
        return [];
    }
  };

  // 过滤列表
  const getFilteredList = () => {
    const list = getCurrentList();
    if (!searchQuery) return list;

    const query = searchQuery.toLowerCase();

    if (activeTab === 'groups') {
      return (list as ChatGroup[]).filter(
        (item) =>
          item.name.toLowerCase().includes(query) ||
          item.description?.toLowerCase().includes(query)
      );
    } else if (activeTab === 'requests') {
      return (list as FriendRequest[]).filter((item) =>
        item.from_user.username.toLowerCase().includes(query)
      );
    } else {
      return (list as ChatContact[]).filter((item) =>
        item.user.username.toLowerCase().includes(query)
      );
    }
  };

  // 格式化时间
  const formatTime = (dateString?: string) => {
    if (!dateString) return t('chat.time.anytime');

    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return t('feed.postCard.justNow');
    if (minutes < 60) return t('feed.postCard.minutesAgo', { count: minutes });
    if (hours < 24) return t('feed.postCard.hoursAgo', { count: hours });
    if (days === 1) return t('time.yesterday');
    if (days < 7) return t('feed.postCard.daysAgo', { count: days });

    return date.toLocaleDateString(i18n.language === 'en' ? 'en-US' : 'zh-CN', { month: '2-digit', day: '2-digit' });
  };

  // 渲染联系人列表项
  const renderContactItem = (contact: ChatContact) => (
    <div
      key={contact.user.id}
      onClick={() => onContactClick(contact)}
      className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors duration-150"
    >
      {/* 头像 */}
      <div className="relative flex-shrink-0">
        {contact.user.avatar ? (
          <img
            src={contact.user.avatar}
            alt={contact.user.username}
            className="w-12 h-12 rounded-full border border-gray-200 object-cover"
          />
        ) : (
          <div className="w-12 h-12 rounded-full border border-gray-200 bg-blue-100 flex items-center justify-center">
            <span className="text-blue-600 font-semibold text-lg">
              {contact.user.username.charAt(0).toUpperCase()}
            </span>
          </div>
        )}

        {/* 在线状态指示器 */}
        {contact.is_online && (
          <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white" />
        )}
      </div>

      {/* 用户信息 */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-0.5">
          <h3
            className={`text-sm truncate ${
              contact.unread_count > 0 ? 'font-bold text-gray-900' : 'font-medium text-gray-700'
            }`}
          >
            {contact.user.username}
          </h3>
          <span className="text-xs text-gray-400 flex-shrink-0 ml-2">
            {formatTime(contact.last_message_time)}
          </span>
        </div>
        {/* 消息预览 */}
        {contact.last_message && (
          <p className={`text-xs truncate mb-0.5 ${contact.unread_count > 0 ? 'text-gray-700 font-medium' : 'text-gray-500'}`}>
            {contact.last_message.from_me && t('chat.selfPrefix')}
            {contact.last_message.content}
          </p>
        )}
        <p className="text-xs text-gray-400 truncate">
          {contact.user.school || ''}
          {contact.user.school && contact.user.major ? ' · ' : ''}
          {contact.user.major || ''}
        </p>
      </div>

      {/* 未读消息气泡 */}
      {contact.unread_count > 0 && (
        <div className="flex-shrink-0 min-w-[20px] h-5 px-1.5 bg-red-500 rounded-full flex items-center justify-center">
          <span className="text-white text-xs font-bold">
            {contact.unread_count > 99 ? t('chat.unread.badge', { count: 99 }) : contact.unread_count}
          </span>
        </div>
      )}
    </div>
  );

  // 渲染群组列表项
  const renderGroupItem = (group: ChatGroup) => (
    <div
      key={group.id}
      onClick={() => onGroupClick(group)}
      className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors duration-150"
    >
      {/* 群组头像 */}
      <div className="flex-shrink-0">
        {group.avatar_url ? (
          <img
            src={group.avatar_url}
            alt={group.name}
            className="w-12 h-12 rounded-lg border border-gray-200 object-cover"
          />
        ) : (
          <div className="w-12 h-12 rounded-lg border border-gray-200 bg-purple-100 flex items-center justify-center">
            <Users className="w-6 h-6 text-purple-600" />
          </div>
        )}
      </div>

      {/* 群组信息 */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-0.5">
          <h3
            className={`text-sm truncate ${
              (group.unread_count || 0) > 0 ? 'font-bold text-gray-900' : 'font-medium text-gray-700'
            }`}
          >
            {group.name}
          </h3>
          <span className="text-xs text-gray-400 flex-shrink-0 ml-2">
            {formatTime(group.last_message_time)}
          </span>
        </div>
        <p className="text-xs text-gray-500 truncate">{t('chat.group.memberCount', { count: group.member_count })}</p>
      </div>

      {/* 未读消息气泡 */}
      {(group.unread_count || 0) > 0 && (
        <div className="flex-shrink-0 min-w-[20px] h-5 px-1.5 bg-red-500 rounded-full flex items-center justify-center">
          <span className="text-white text-xs font-bold">
            {group.unread_count! > 99 ? t('chat.unread.badge', { count: 99 }) : group.unread_count}
          </span>
        </div>
      )}
    </div>
  );

  // 渲染好友申请列表项
  const renderRequestItem = (request: FriendRequest) => (
    <div key={request.id} className="flex items-center gap-3 px-4 py-3 border-b border-gray-100">
      {/* 申请人头像 */}
      <div className="flex-shrink-0">
        {request.from_user.avatar ? (
          <img
            src={request.from_user.avatar}
            alt={request.from_user.username}
            className="w-12 h-12 rounded-full border border-gray-200 object-cover"
          />
        ) : (
          <div className="w-12 h-12 rounded-full border border-gray-200 bg-blue-100 flex items-center justify-center">
            <span className="text-blue-600 font-semibold text-lg">
              {request.from_user.username.charAt(0).toUpperCase()}
            </span>
          </div>
        )}
      </div>

      {/* 申请人信息 */}
      <div className="flex-1 min-w-0">
        <h3 className="text-sm font-medium text-gray-700 truncate mb-0.5">
          {request.from_user.username}
        </h3>
        <p className="text-xs text-gray-500 truncate">
          {request.from_user.school || ''}
          {request.from_user.school && request.from_user.major ? ' · ' : ''}
          {request.from_user.major || ''}
        </p>
        <p className="text-xs text-gray-400 mt-0.5">{formatTime(request.created_at)}</p>
      </div>

      {/* 操作按钮 */}
      <div className="flex gap-2 flex-shrink-0">
        <button
          className="px-3 py-1.5 bg-blue-500 text-white text-xs rounded-md hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          onClick={(e) => {
            e.stopPropagation();
            onAcceptRequest(request.id);
          }}
        >
          {t('chat.actions.accept')}
        </button>
        <button
          className="px-3 py-1.5 bg-gray-200 text-gray-700 text-xs rounded-md hover:bg-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          onClick={(e) => {
            e.stopPropagation();
            onRejectRequest(request.id);
          }}
        >
          {t('chat.actions.reject')}
        </button>
      </div>
    </div>
  );

  // 渲染列表内容
  const renderListContent = () => {
    if (isLoading) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-400 text-sm">{t('common.loading')}</div>
        </div>
      );
    }

    const filteredList = getFilteredList();

    if (filteredList.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center h-64">
          <MessageCircle className="w-12 h-12 text-gray-300 mb-3" />
          <p className="text-sm text-gray-400">{t(`chat.empty.${activeTab}`)}</p>
        </div>
      );
    }

    return (
      <div className="divide-y divide-gray-100">
        {activeTab === 'groups'
          ? (filteredList as ChatGroup[]).map(renderGroupItem)
          : activeTab === 'requests'
          ? (filteredList as FriendRequest[]).map(renderRequestItem)
          : (filteredList as ChatContact[]).map(renderContactItem)}
      </div>
    );
  };

  return (
    <>
      {/* 遮罩层 */}
      <div className="fixed inset-0 bg-black bg-opacity-20 z-40" onClick={onClose} />

      {/* 弹窗 */}
      <div className="fixed bottom-24 left-6 w-[400px] h-[600px] bg-white rounded-xl shadow-2xl z-50 flex flex-col animate-slide-up">
        {/* 标题栏 */}
        <div className="flex items-center justify-between px-4 h-14 border-b border-gray-200 flex-shrink-0">
          <h2 className="text-base font-bold text-gray-900">{t('chat.title')}</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-full transition-colors duration-150"
            aria-label="Close"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Tab 栏 */}
        <div className="flex border-b border-gray-200 flex-shrink-0">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => onTabChange(tab.key)}
              className={`flex-1 py-3 text-sm font-medium transition-colors duration-150 relative ${
                activeTab === tab.key
                  ? 'text-blue-500'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.label} ({tab.count})
              {activeTab === tab.key && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500" />
              )}
              {/* 未读请求红点 */}
              {tab.key === 'requests' && tab.count > 0 && activeTab !== 'requests' && (
                <div className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full" />
              )}
            </button>
          ))}
        </div>

        {/* 搜索框 */}
        <div className="px-4 py-3 flex-shrink-0">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder={t('chat.search.placeholder')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-gray-100 border-none rounded-lg text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* 列表区域 */}
        <div className="flex-1 overflow-y-auto">
          {renderListContent()}
        </div>
      </div>
    </>
  );
};

export default ChatDrawer;
