import React, { useState, useRef, useEffect } from 'react';
import { ArrowLeft, MoreVertical, Send, Smile, Image, Plus } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { UserBasic, ChatGroup, ChatMessage } from '@/types/chat';

interface ChatViewProps {
  recipient?: UserBasic;
  group?: ChatGroup;
  messages: ChatMessage[];
  currentUserId: number;
  onBack: () => void;
  onSendMessage: (content: string) => void;
  isLoading: boolean;
}

const ChatView: React.FC<ChatViewProps> = ({
  recipient,
  group,
  messages,
  currentUserId,
  onBack,
  onSendMessage,
  isLoading,
}) => {
  const { t } = useTranslation();
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 调整输入框高度
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 120) + 'px';
    }
  }, [inputValue]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = () => {
    if (inputValue.trim() === '') return;

    onSendMessage(inputValue.trim());
    setInputValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // 格式化时间
  const formatMessageTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const messageDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

    const timeStr = date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });

    if (messageDate.getTime() === today.getTime()) {
      return timeStr;
    } else if (messageDate.getTime() === today.getTime() - 86400000) {
      return `昨天 ${timeStr}`;
    } else {
      return date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      });
    }
  };

  // 判断是否需要显示日期分隔线
  const shouldShowDateSeparator = (index: number) => {
    if (index === 0) return true;

    const currentDate = new Date(messages[index].created_at).toDateString();
    const prevDate = new Date(messages[index - 1].created_at).toDateString();

    return currentDate !== prevDate;
  };

  // 获取日期分隔线文本
  const getDateSeparatorText = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const messageDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

    if (messageDate.getTime() === today.getTime()) {
      return '今天';
    } else if (messageDate.getTime() === today.getTime() - 86400000) {
      return '昨天';
    } else {
      return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' });
    }
  };

  // 渲染消息气泡
  const renderMessage = (message: ChatMessage, index: number) => {
    const isOwnMessage = message.from_user.id === currentUserId;

    return (
      <div key={message.id}>
        {/* 日期分隔线 */}
        {shouldShowDateSeparator(index) && (
          <div className="flex items-center justify-center my-4">
            <div className="px-3 py-1 bg-gray-100 rounded-full text-xs text-gray-500">
              {getDateSeparatorText(message.created_at)}
            </div>
          </div>
        )}

        {/* 消息气泡 */}
        <div className={`flex items-end gap-2 mb-4 ${isOwnMessage ? 'flex-row-reverse' : 'flex-row'}`}>
          {/* 对方头像 (群聊且不是自己的消息时显示) */}
          {!isOwnMessage && group && (
            <div className="flex-shrink-0">
              {message.from_user.avatar ? (
                <img
                  src={message.from_user.avatar}
                  alt={message.from_user.username}
                  className="w-8 h-8 rounded-full border border-gray-200 object-cover"
                />
              ) : (
                <div className="w-8 h-8 rounded-full border border-gray-200 bg-blue-100 flex items-center justify-center">
                  <span className="text-blue-600 font-semibold text-xs">
                    {message.from_user.username.charAt(0).toUpperCase()}
                  </span>
                </div>
              )}
            </div>
          )}

          {/* 消息内容 */}
          <div className={`flex flex-col max-w-[70%] ${isOwnMessage ? 'items-end' : 'items-start'}`}>
            {/* 发送者名字 (群聊且不是自己时显示) */}
            {!isOwnMessage && group && (
              <span className="text-xs text-gray-500 mb-1 px-1">{message.from_user.username}</span>
            )}

            {/* 消息气泡 */}
            <div
              className={`px-4 py-2.5 rounded-2xl ${
                isOwnMessage
                  ? 'bg-blue-500 text-white rounded-br-sm'
                  : 'bg-white text-gray-900 rounded-bl-sm border border-gray-200'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
            </div>

            {/* 时间戳 */}
            <span
              className={`text-xs text-gray-400 mt-1 px-1 ${isOwnMessage ? 'text-right' : 'text-left'}`}
            >
              {formatMessageTime(message.created_at)}
            </span>
          </div>
        </div>
      </div>
    );
  };

  const displayName = recipient?.username || group?.name || '';
  const isOnline = recipient ? true : false; // TODO: 从实际在线状态获取
  const lastSeenText = isOnline ? '在线' : '上次在线：2小时前'; // TODO: 从实际数据获取

  return (
    <div className="fixed bottom-24 left-6 w-[400px] h-[600px] bg-white rounded-xl shadow-2xl z-50 flex flex-col animate-slide-up">
      {/* 顶部信息栏 */}
      <div className="flex items-center gap-3 px-4 h-16 border-b border-gray-200 flex-shrink-0">
        {/* 返回按钮 */}
        <button
          onClick={onBack}
          className="p-1 hover:bg-gray-100 rounded-full transition-colors duration-150"
          aria-label="Back"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>

        {/* 头像 */}
        <div className="flex-shrink-0">
          {recipient?.avatar || group?.avatar_url ? (
            <img
              src={recipient?.avatar || group?.avatar_url}
              alt={displayName}
              className={`w-10 h-10 object-cover border border-gray-200 ${
                recipient ? 'rounded-full' : 'rounded-lg'
              }`}
            />
          ) : (
            <div
              className={`w-10 h-10 border border-gray-200 ${
                recipient ? 'bg-blue-100 rounded-full' : 'bg-purple-100 rounded-lg'
              } flex items-center justify-center`}
            >
              <span className={`${recipient ? 'text-blue-600' : 'text-purple-600'} font-semibold text-sm`}>
                {displayName.charAt(0).toUpperCase()}
              </span>
            </div>
          )}
        </div>

        {/* 用户/群组信息 */}
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-gray-900 truncate">{displayName}</h3>
          <p className="text-xs text-gray-500 truncate">
            {recipient ? lastSeenText : `${group?.member_count} 成员`}
          </p>
        </div>

        {/* 更多操作按钮 */}
        <button
          className="p-1 hover:bg-gray-100 rounded-full transition-colors duration-150"
          aria-label="More options"
        >
          <MoreVertical className="w-5 h-5 text-gray-600" />
        </button>
      </div>

      {/* 消息显示区 */}
      <div className="flex-1 overflow-y-auto px-4 py-4 bg-gray-50">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-gray-400 text-sm">加载消息中...</div>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="text-gray-400 text-sm mb-2">{t('chat.messages.no_messages')}</div>
              <div className="text-gray-300 text-xs">{recipient?.username || group?.name}</div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => renderMessage(message, index))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* 消息输入区 */}
      <div className="border-t border-gray-200 bg-white flex-shrink-0">
        {/* 工具栏 */}
        <div className="flex items-center gap-2 px-4 py-2">
          <button
            className="p-1.5 hover:bg-gray-100 rounded-full transition-colors duration-150"
            aria-label="Add emoji"
          >
            <Smile className="w-5 h-5 text-gray-500" />
          </button>
          <button
            className="p-1.5 hover:bg-gray-100 rounded-full transition-colors duration-150"
            aria-label="Add image"
          >
            <Image className="w-5 h-5 text-gray-500" />
          </button>
          <button
            className="p-1.5 hover:bg-gray-100 rounded-full transition-colors duration-150"
            aria-label="More options"
          >
            <Plus className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* 输入框和发送按钮 */}
        <div className="flex items-end gap-2 px-4 pb-4">
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={t('chat.input.placeholder')}
            rows={1}
            className="flex-1 px-3 py-2 bg-gray-100 border-none rounded-xl text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 max-h-[120px]"
          />
          <button
            onClick={handleSend}
            disabled={inputValue.trim() === ''}
            className={`p-2.5 rounded-lg transition-colors duration-150 flex-shrink-0 ${
              inputValue.trim() === ''
                ? 'bg-gray-200 cursor-not-allowed'
                : 'bg-blue-500 hover:bg-blue-600'
            }`}
            aria-label="Send message"
          >
            <Send className={`w-5 h-5 ${inputValue.trim() === '' ? 'text-gray-400' : 'text-white'}`} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatView;
