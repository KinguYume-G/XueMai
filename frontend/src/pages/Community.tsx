import { useState, useEffect, useCallback } from 'react'
import { Users } from 'lucide-react'
import CreatePostBox from '@/components/feed/CreatePostBox'
import FeedTabs from '@/components/feed/FeedTabs'
import PostCard from '@/components/feed/PostCard'
import { postsApi } from '@/services/api/posts'
import { tagsApi } from '@/services/api/tags'
import { parseApiError } from '@/lib/api/error'
import { Badge } from '@/components/ui/badge'
import type { Post, Tag } from '@/types/api'

export default function Community() {
  const [activeTab, setActiveTab] = useState<'hot' | 'new' | 'follow'>('new')
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tags, setTags] = useState<Tag[]>([])
  const [selectedTag, setSelectedTag] = useState<string | null>(null)

  // 加载所有标签
  useEffect(() => {
    const loadTags = async () => {
      try {
        const allTags = await tagsApi.getAllTags()
        setTags(allTags)
      } catch (err) {
        console.error('Failed to load tags:', err)
      }
    }
    loadTags()
  }, [])

  const fetchFeed = useCallback(async (tab: 'hot' | 'new' | 'follow', page: number, tagFilter?: string | null) => {
    try {
      setLoading(true)
      setError(null)

      // 使用 Feed API 获取数据，支持标签筛选
      const params: any = { tab, page }
      if (tagFilter) {
        params.tags = tagFilter
      }

      const response = await postsApi.getFeed(params)

      // apiClient interceptor 已解包，response 可能是 Post[] 或 { data: Post[], paging: {...} }
      let postsData: any[] = []
      if (Array.isArray(response)) {
        postsData = response
      } else if (response && typeof response === 'object') {
        postsData = (response as any).data || (response as any).results || []
      }

      // 映射数据格式（与 Home 页面相同的逻辑）
      const mappedPosts = postsData.map((item: any) => {
        // 处理 author
        let authorId: number
        let authorUsername: string
        let authorAvatar: string | undefined

        if (item.author && typeof item.author === 'object') {
          authorId = item.author.id || item.author_id || item.author
          authorUsername = item.author.username || item.author_username || '未命名用户'
          authorAvatar = item.author.avatar || item.author.avatar_url || item.author_avatar
        } else {
          authorId = item.author || item.author_id || 0
          authorUsername = item.author_username || '未命名用户'
          authorAvatar = item.author_avatar
        }

        // 处理 tags
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
    fetchFeed(activeTab, 1, selectedTag)
  }, [activeTab, selectedTag, fetchFeed])

  const handlePostCreated = useCallback(() => {
    setActiveTab('new')
    setSelectedTag(null)
    fetchFeed('new', 1, null)
  }, [fetchFeed])

  const handleTagClick = (tagSlug: string) => {
    if (selectedTag === tagSlug) {
      setSelectedTag(null)
    } else {
      setSelectedTag(tagSlug)
    }
  }

  return (
    <div className="space-y-4">
      {/* Page Header */}
      <div className="bg-white rounded-2xl border shadow-sm p-6">
        <div className="flex items-center gap-3">
          <div className="rounded-full bg-primary/10 p-2">
            <Users className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">社区</h1>
            <p className="text-sm text-muted-foreground">
              分享见解，交流想法
            </p>
          </div>
        </div>
      </div>

      {/* Create Post Box */}
      <CreatePostBox onPostCreated={handlePostCreated} />

      {/* Tag Filter Pills */}
      {tags.length > 0 && (
        <div className="bg-white rounded-2xl border shadow-sm p-4">
          <div className="flex items-center gap-2 overflow-x-auto pb-2">
            <span className="text-sm text-muted-foreground shrink-0">标签筛选:</span>
            <Badge
              variant={selectedTag === null ? 'default' : 'outline'}
              className="cursor-pointer shrink-0"
              onClick={() => setSelectedTag(null)}
            >
              全部
            </Badge>
            {tags.map((tag) => (
              <Badge
                key={tag.id}
                variant={selectedTag === tag.slug ? 'default' : 'outline'}
                className="cursor-pointer shrink-0"
                onClick={() => handleTagClick(tag.slug)}
              >
                #{tag.name}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Feed Section */}
      <div className="bg-white rounded-2xl border shadow-sm overflow-hidden">
        <FeedTabs activeTab={activeTab} onTabChange={setActiveTab as (tab: string) => void} />

        {/* Posts List */}
        <div className="divide-y">
          {loading ? (
            <div className="p-8 text-center text-muted-foreground">
              加载中...
            </div>
          ) : error ? (
            <div className="p-8 text-center">
              <p className="text-sm text-destructive mb-2">{error}</p>
              <button
                onClick={() => fetchFeed(activeTab, 1, selectedTag)}
                className="text-sm text-primary hover:underline"
              >
                重试
              </button>
            </div>
          ) : posts.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              {selectedTag
                ? '该标签下暂无内容'
                : activeTab === 'follow'
                ? '暂无关注的人发布内容'
                : '暂无内容，快来发布第一条帖子吧！'}
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
