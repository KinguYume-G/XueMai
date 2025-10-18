import React, { useState } from 'react';
import CreatePostBox from '../components/feed/CreatePostBox';
import FeedContainer from '../components/feed/FeedContainer';
import FeedTabs from '../components/feed/FeedTabs';

const Home: React.FC = () => {
  const [activeTab, setActiveTab] = useState('recommended');
  const [autoTranslate, setAutoTranslate] = useState(false);

  const handlePost = (content: string, images: File[]) => {
    console.log('New post:', { content, images });
    // 这里可以添加发布帖子的逻辑
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Create Post Box */}
      <CreatePostBox 
        onPost={handlePost}
        userAvatar="/placeholder-avatar.jpg"
        userName="张小明"
      />

      {/* Feed Tabs */}
      <FeedTabs
        activeTab={activeTab}
        onTabChange={setActiveTab}
        autoTranslate={autoTranslate}
        onToggleTranslate={() => setAutoTranslate(!autoTranslate)}
      />

      {/* Feed Container */}
      <FeedContainer />
    </div>
  );
};

export default Home;
