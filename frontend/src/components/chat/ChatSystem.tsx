import React from 'react';
import { useTranslation } from 'react-i18next';
import FloatingActions from './FloatingActions';
import ChatDrawer from './ChatDrawer';
import ChatView from './ChatView';
import useChatStore from '@/store/useChatStore';
import { useAuthStore } from '@/store/authStore';

const ChatSystem: React.FC = () => {
  const { i18n } = useTranslation();
  const { user } = useAuthStore();

  const {
    isOpen,
    setOpen,
    activeTab,
    setActiveTab,
    followingList,
    followersList,
    friendsList,
    groupsList,
    requestsList,
    selectedUser,
    selectedGroup,
    messages,
    unreadCount,
    isLoading,
    selectUser,
    selectGroup,
    backToList,
    sendMessage,
    acceptRequest,
    rejectRequest,
  } = useChatStore();

  // 语言切换处理
  const handleLanguageChange = (lang: 'zh' | 'en') => {
    i18n.changeLanguage(lang);
    localStorage.setItem('language', lang);
  };

  // 检查用户是否已登录
  if (!user) {
    return null; // 未登录时不显示聊天按钮
  }

  return (
    <>
      {/* 左下角功能按钮组 */}
      <FloatingActions
        unreadCount={unreadCount}
        onChatClick={() => setOpen(true)}
        currentLanguage={i18n.language as 'zh' | 'en'}
        onLanguageChange={handleLanguageChange}
      />

      {/* 聊天弹窗或聊天界面 */}
      {selectedUser || selectedGroup ? (
        // 显示聊天界面
        <ChatView
          recipient={selectedUser || undefined}
          group={selectedGroup || undefined}
          messages={messages}
          currentUserId={user.id}
          onBack={backToList}
          onSendMessage={sendMessage}
          isLoading={isLoading}
        />
      ) : (
        // 显示联系人列表
        <ChatDrawer
          isOpen={isOpen}
          onClose={() => setOpen(false)}
          activeTab={activeTab}
          onTabChange={setActiveTab}
          followingList={followingList}
          followersList={followersList}
          friendsList={friendsList}
          groupsList={groupsList}
          requestsList={requestsList}
          onContactClick={(contact) => selectUser(contact.user)}
          onGroupClick={selectGroup}
          onAcceptRequest={acceptRequest}
          onRejectRequest={rejectRequest}
          isLoading={isLoading}
        />
      )}
    </>
  );
};

export default ChatSystem;
