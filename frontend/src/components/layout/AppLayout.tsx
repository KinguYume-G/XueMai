import React from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import RightPanel from './RightPanel';

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
        <div className="hidden lg:block lg:w-60 lg:fixed lg:left-0 lg:top-16 lg:h-[calc(100vh-4rem)] lg:overflow-y-auto">
          <Sidebar />
        </div>
        
        {/* Main Content */}
        <div className="flex-1 lg:ml-60 lg:mr-80">
          <div className="max-w-2xl mx-auto px-4 py-6">
            {children}
          </div>
        </div>
        
        {/* Right Panel */}
        <div className="hidden xl:block xl:w-80 xl:fixed xl:right-0 xl:top-16 xl:h-[calc(100vh-4rem)] xl:overflow-y-auto">
          <RightPanel />
        </div>
      </div>
    </div>
  );
};

export default AppLayout;
