import React from 'react';
import { MessageCircle } from 'lucide-react';

interface FloatingActionsProps {
  unreadCount: number;
  onChatClick: () => void;
  currentLanguage: 'zh' | 'en';
  onLanguageChange: (lang: 'zh' | 'en') => void;
}

const FloatingActions: React.FC<FloatingActionsProps> = ({
  unreadCount,
  onChatClick,
  currentLanguage,
  onLanguageChange,
}) => {
  return (
    <div className="fixed bottom-6 left-6 z-50 flex flex-col gap-3">
      {/* 聊天按钮 */}
      <div className="relative">
        <button
          onClick={onChatClick}
          className="w-15 h-15 rounded-full bg-blue-500 shadow-lg hover:bg-blue-600 transition-all duration-200 hover:scale-105 active:scale-95 flex items-center justify-center group"
          aria-label="Open chat"
        >
          <MessageCircle className="w-6 h-6 text-white" />
        </button>

        {/* 未读消息气泡 */}
        {unreadCount > 0 && (
          <div className="absolute -top-1 -right-1 min-w-[20px] h-5 px-1.5 bg-red-500 rounded-full flex items-center justify-center">
            <span className="text-white text-xs font-bold">
              {unreadCount > 99 ? '99+' : unreadCount}
            </span>
          </div>
        )}
      </div>

      {/* 语言切换按钮 */}
      <div className="flex bg-white rounded-lg shadow-md overflow-hidden">
        <button
          onClick={() => onLanguageChange('zh')}
          className={`w-[50px] h-10 text-sm font-medium transition-all duration-200 ${
            currentLanguage === 'zh'
              ? 'bg-blue-50 text-blue-500 font-bold'
              : 'bg-white text-gray-600 hover:bg-gray-50'
          }`}
          aria-label="Switch to Chinese"
        >
          中
        </button>
        <button
          onClick={() => onLanguageChange('en')}
          className={`w-[50px] h-10 text-sm font-medium transition-all duration-200 ${
            currentLanguage === 'en'
              ? 'bg-blue-50 text-blue-500 font-bold'
              : 'bg-white text-gray-600 hover:bg-gray-50'
          }`}
          aria-label="Switch to English"
        >
          EN
        </button>
      </div>
    </div>
  );
};

export default FloatingActions;
