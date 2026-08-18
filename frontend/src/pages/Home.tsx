import { useState, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import CreatePostBox from '@/components/feed/CreatePostBox'
import FeedTabs from '@/components/feed/FeedTabs'
import PostCard from '@/components/feed/PostCard'
import { postsApi } from '@/services/api/posts'
import { parseApiError } from '@/lib/api/error'
import type { Post } from '@/types/api'

export default function Home() {
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState<'hot' | 'new' | 'follow'>('new')
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchFeed = useCallback(async (tab: 'hot' | 'new' | 'follow', page: number) => {
    try {
      setLoading(true)
      setError(null)
      
      // 使用 Feed API 获取数据
      // 注意：apiClient 的 interceptor 已经解包了 { data: [...], paging: {...} }，返回的是 data 数组
      const response = await postsApi.getFeed({ tab, page })
      
      // apiClient interceptor 已解包，response 可能是 Post[] 或 { data: Post[], paging: {...} }
      // 需要兼容两种情况
      let postsData: any[] = []
      if (Array.isArray(response)) {
        // 如果 interceptor 解包了，response 就是 Post[]
        postsData = response
      } else if (response && typeof response === 'object') {
        // 如果返回的是对象，尝试从 data 或 results 字段读取
        postsData = (response as any).data || (response as any).results || []
      }
      
      // 调试日志（开发环境）
      if (import.meta.env.DEV) {
        console.log(`[Feed] tab=${tab}, page=${page}, posts count:`, postsData.length)
        if (postsData.length > 0) {
          console.log('[Feed] First post:', postsData[0])
        }
      }
      
      // 映射数据格式（后端返回 author 是对象，tags 是对象数组）
      const mappedPosts = postsData.map((item: any) => {
        // 处理 author：后端返回的是 UserSerializer 对象
        let authorId: number
        let authorUsername: string
        let authorAvatar: string | undefined
        
        if (item.author && typeof item.author === 'object') {
          // author 是对象，提取 id 和 username
          authorId = item.author.id || item.author_id || item.author
          authorUsername = item.author.username || item.author_username || t('feed.home.unnamedUser')
          authorAvatar = item.author.avatar || item.author.avatar_url || item.author_avatar
        } else {
          // author 可能是 ID（理论上不应该发生，但兼容处理）
          authorId = item.author || item.author_id || 0
          authorUsername = item.author_username || t('feed.home.unnamedUser')
          authorAvatar = item.author_avatar
        }
        
        // 处理 tags：后端返回的是 TagSerializer 数组
        const tagsArray = Array.isArray(item.tags) ? item.tags : []
        const tagIds = tagsArray.map((tag: any) => 
          typeof tag === 'object' ? tag.id : tag
        )
        const tagsData = tagsArray.map((tag: any) => {
          if (typeof tag === 'object') {
            return {
              id: tag.id,
              name: tag.name || '',
              slug: tag.slug || '',
              posts_count: tag.posts_count || 0,
              created_at: tag.created_at || '',
            }
          }
          return null
        }).filter(Boolean) as any[]
        
        return {
          id: item.id,
          author: authorId,
          author_username: authorUsername,
          author_avatar: authorAvatar,
          title: item.title || '',
          body: item.body || item.content || '',
          image_url: item.image_url,
          video_url: item.video_url,
          visibility: item.visibility || 'public',
          is_published: item.is_published !== undefined ? item.is_published : true,
          target_university: item.target_university,
          target_school: item.target_school,
          tags: tagIds,
          tags_data: tagsData,
          likes_count: item.likes_count || 0,
          comments_count: item.comments_count || 0,
          bookmarks_count: item.bookmarks_count || 0,
          views_count: item.views_count || 0,
          is_liked: item.is_liked || false,
          is_bookmarked: item.is_bookmarked || false,
          created_at: item.created_at,
          updated_at: item.updated_at || item.created_at,
        }
      }) as Post[]
      
      setPosts(mappedPosts)
    } catch (err) {
      console.error('Failed to load posts:', err)
      setError(parseApiError(err))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchFeed(activeTab, 1)
  }, [activeTab, fetchFeed])

  const handlePostCreated = useCallback(() => {
    // 发帖成功后强制切换到"最新"tab并重新拉取 Feed，确保新帖立即显示
    setActiveTab('new')
    fetchFeed('new', 1)
  }, [fetchFeed])

  return (
    <div className="space-y-4">
      {/* Create Post Box */}
      <CreatePostBox onPostCreated={handlePostCreated} />

      {/* Feed Tabs */}
      <div className="bg-white rounded-2xl border shadow-sm overflow-hidden">
        <FeedTabs activeTab={activeTab} onTabChange={setActiveTab as (tab: string) => void} />
        
        {/* Posts List */}
        <div className="divide-y">
          {loading ? (
            <div className="p-8 text-center text-muted-foreground">
              {t('feed.home.loading')}
            </div>
          ) : error ? (
            <div className="p-8 text-center">
              <p className="text-sm text-destructive mb-2">{error}</p>
              <button
                onClick={() => fetchFeed(activeTab, 1)}
                className="text-sm text-primary hover:underline"
              >
                {t('common.retry')}
              </button>
            </div>
          ) : posts.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              {activeTab === 'follow' ? t('feed.home.emptyFollow') : t('feed.home.emptyDefault')}
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

