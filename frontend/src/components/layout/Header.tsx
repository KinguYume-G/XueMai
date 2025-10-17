import React from 'react';
import { Search, Bell, MessageCircle, Plus } from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import SearchBar from '../common/SearchBar';
import UserDropdown from '../profile/UserDropdown';

const Header: React.FC = () => {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white shadow-sm border-b">
      <div className="h-16 flex items-center justify-between px-6">
        {/* Logo */}
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">学</span>
          </div>
          <span className="text-xl font-bold text-gray-900">学脉 | UniPulse Asia</span>
        </div>

        {/* Search Bar - Hidden on mobile */}
        <div className="hidden md:block flex-1 max-w-3xl mx-12">
          <SearchBar 
            onSearch={(query) => console.log('Search:', query)}
            placeholder="搜索同学、话题、课程、职位..."
          />
        </div>

        {/* Right Side Icons */}
        <div className="flex items-center space-x-4">
          {/* Mobile Search Icon */}
          <Button variant="ghost" size="sm" className="md:hidden">
            <Search className="h-5 w-5" />
          </Button>

          {/* Notifications */}
          <Button variant="ghost" size="sm" className="relative">
            <Bell className="h-5 w-5" />
            <Badge 
              variant="destructive" 
              className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 text-xs flex items-center justify-center"
            >
              3
            </Badge>
          </Button>

          {/* Messages */}
          <Button variant="ghost" size="sm" className="relative">
            <MessageCircle className="h-5 w-5" />
            <Badge 
              variant="destructive" 
              className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 text-xs flex items-center justify-center"
            >
              1
            </Badge>
          </Button>

          {/* Create Button */}
          <Button className="bg-blue-600 hover:bg-blue-700 text-white">
            <Plus className="h-4 w-4 mr-2" />
            创建
          </Button>

          {/* User Dropdown */}
          <UserDropdown
            userAvatar="/placeholder-avatar.jpg"
            userName="张小明"
            userEmail="zhangxiaoming@example.com"
            onProfileClick={() => console.log('Profile clicked')}
            onSettingsClick={() => console.log('Settings clicked')}
            onHelpClick={() => console.log('Help clicked')}
            onLogoutClick={() => console.log('Logout clicked')}
          />
        </div>
      </div>
    </header>
  );
};

export default Header;
