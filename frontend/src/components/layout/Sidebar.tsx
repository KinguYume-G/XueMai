import React from 'react';
import { 
  Home, 
  FileText, 
  Users, 
  Briefcase, 
  Briefcase as JobIcon, 
  Lightbulb, 
  Wrench, 
  Building,
  Clock,
  FileText as SubscribedIcon,
  Bookmark,
  Sun,
  Moon
} from 'lucide-react';
import { Button } from '../ui/button';
import { useState } from 'react';
import ThemeToggle from '../common/ThemeToggle';
import LanguageSwitch from '../common/LanguageSwitch';

interface SidebarProps {
  className?: string;
}

const Sidebar: React.FC<SidebarProps> = ({ className }) => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  const mainMenuItems = [
    { icon: Home, label: '主页', href: '/', active: true },
    { icon: FileText, label: '专业论坛', href: '/forums' },
    { icon: Users, label: '社区', href: '/community' },
    { icon: Briefcase, label: '交换项目', href: '/exchange' },
    { icon: JobIcon, label: '实习 & 职位', href: '/jobs' },
    { icon: Lightbulb, label: '创业/悬赏', href: '/startup' },
    { icon: Wrench, label: 'AI 工具箱', href: '/ai' },
    { icon: Building, label: '关于 APU/高校', href: '/about' },
  ];

  const secondaryItems = [
    { icon: Clock, label: '最近访问', href: '/recent' },
    { icon: SubscribedIcon, label: '已订阅', href: '/subscribed' },
    { icon: Bookmark, label: '收藏', href: '/bookmarks' },
  ];

  return (
    <div className={`bg-white h-full ${className}`}>
      <div className="p-4 space-y-6">
        {/* Main Menu */}
        <nav className="space-y-1">
          {mainMenuItems.map((item, index) => (
            <Button
              key={index}
              variant={item.active ? "default" : "ghost"}
              className={`w-full justify-start h-10 px-4 ${
                item.active 
                  ? 'bg-blue-50 text-blue-600 hover:bg-blue-100' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
              asChild
            >
              <a href={item.href} className="flex items-center space-x-3">
                <item.icon className="h-5 w-5" />
                <span className="text-sm font-medium">{item.label}</span>
              </a>
            </Button>
          ))}
        </nav>

        {/* Secondary Section */}
        <div className="pt-4 border-t">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 px-3">
            次级
          </h3>
          <nav className="space-y-1">
            {secondaryItems.map((item, index) => (
              <Button
                key={index}
                variant="ghost"
                className="w-full justify-start h-10 px-4 text-gray-600 hover:bg-gray-100"
                asChild
              >
                <a href={item.href} className="flex items-center space-x-3">
                  <item.icon className="h-4 w-4" />
                  <span className="text-sm">{item.label}</span>
                </a>
              </Button>
            ))}
          </nav>
        </div>

        {/* Bottom Controls */}
        <div className="pt-4 border-t space-y-3">
          {/* Theme Toggle */}
          <div className="flex items-center justify-between px-3">
            <div className="flex items-center space-x-2">
              <Sun className="h-4 w-4 text-gray-500" />
              <Moon className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">主题</span>
            </div>
            <ThemeToggle showLabel={false} size="sm" />
          </div>

          {/* Language Switch */}
          <div className="flex items-center justify-between px-3">
            <span className="text-sm text-gray-600">语言</span>
            <LanguageSwitch showLabel={false} size="sm" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
