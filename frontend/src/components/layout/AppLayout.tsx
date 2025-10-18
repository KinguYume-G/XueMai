import React from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import RightPanel from './RightPanel';
import { Bot } from 'lucide-react';
import { Button } from '../ui/button';

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header />
      
      <div className="flex pt-16">
        {/* Left Sidebar */}
        <div className="hidden lg:block lg:w-64 lg:fixed lg:left-0 lg:top-16 lg:h-[calc(100vh-4rem)] lg:overflow-y-auto lg:bg-white lg:border-r lg:shadow-sm">
          <Sidebar />
        </div>
        
        {/* Main Content */}
        <div className="flex-1 lg:ml-64 xl:mr-80">
          <div className="max-w-3xl mx-auto px-4 py-6">
            {children}
          </div>
        </div>
        
        {/* Right Panel */}
        <div className="hidden xl:block xl:w-80 xl:fixed xl:right-0 xl:top-16 xl:h-[calc(100vh-4rem)] xl:overflow-y-auto xl:bg-white xl:border-l xl:shadow-sm">
          <RightPanel />
        </div>
      </div>

      {/* Floating AI Assistant Button */}
      <div className="fixed bottom-6 right-6 z-50">
        <Button
          size="lg"
          className="h-14 w-14 rounded-full bg-blue-600 hover:bg-blue-700 shadow-lg hover:shadow-xl transition-all duration-200"
        >
          <Bot className="h-6 w-6" />
        </Button>
      </div>
    </div>
  );
};

export default AppLayout;
