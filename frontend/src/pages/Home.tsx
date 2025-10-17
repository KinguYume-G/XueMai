import React, { useState } from 'react';
import FeedContainer from '../components/feed/FeedContainer';
import FeedTabs from '../components/feed/FeedTabs';

const Home: React.FC = () => {
  const [activeTab, setActiveTab] = useState('recommended');
  const [autoTranslate, setAutoTranslate] = useState(false);

  return (
    <div className="max-w-2xl mx-auto">
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
