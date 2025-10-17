import React from 'react';
import { Button } from '../ui/button';
import { Switch } from '../ui/switch';

interface FeedTabsProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  autoTranslate: boolean;
  onToggleTranslate: () => void;
}

const FeedTabs: React.FC<FeedTabsProps> = ({
  activeTab,
  onTabChange,
  autoTranslate,
  onToggleTranslate
}) => {
  const tabs = [
    { id: 'recommended', label: '推荐' },
    { id: 'latest', label: '最新' },
    { id: 'following', label: '关注' },
  ];

  return (
    <div className="flex items-center justify-between mb-6">
      {/* Tabs */}
      <div className="flex items-center space-x-6">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`relative pb-2 text-sm font-medium transition-colors duration-200 ${
              activeTab === tab.id
                ? 'text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.label}
            {activeTab === tab.id && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 rounded-full" />
            )}
          </button>
        ))}
      </div>

      {/* Auto Translate Toggle */}
      <div className="flex items-center space-x-2">
        <span className="text-sm text-gray-600">自动翻译</span>
        <Switch
          checked={autoTranslate}
          onCheckedChange={onToggleTranslate}
        />
      </div>
    </div>
  );
};

export default FeedTabs;
