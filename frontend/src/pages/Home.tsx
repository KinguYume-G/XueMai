import { useState, useEffect } from 'react'
import CreatePostBox from '@/components/feed/CreatePostBox'
import FeedTabs from '@/components/feed/FeedTabs'
import PostCard from '@/components/feed/PostCard'
import { getPosts } from '@/services/mock'
import type { Post } from '@/types/post'

export default function Home() {
  const [activeTab, setActiveTab] = useState('recommend')
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getPosts()
      .then(setPosts)
      .finally(() => setLoading(false))
  }, [activeTab])

  return (
    <div className="space-y-4">
      {/* Create Post Box */}
      <CreatePostBox />

      {/* Feed Tabs */}
      <div className="bg-white rounded-2xl border shadow-sm overflow-hidden">
        <FeedTabs activeTab={activeTab} onTabChange={setActiveTab} />
        
        {/* Posts List */}
        <div className="divide-y">
          {loading ? (
            <div className="p-8 text-center text-muted-foreground">
              加载中...
            </div>
          ) : posts.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              暂无内容
            </div>
          ) : (
            posts.map((post) => (
              <div key={post.id} className="p-0">
                <PostCard post={post} />
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

