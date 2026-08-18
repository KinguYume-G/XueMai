import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useBookmarkStore } from '@/store/useBookmarkStore'
import PostCard from '@/components/feed/PostCard'
import { BookmarkedExchangeCard } from '@/components/bookmarks/BookmarkedExchangeCard'
import { BookmarkedInternshipCard } from '@/components/bookmarks/BookmarkedInternshipCard'
import { BookmarkedCommunityCard } from '@/components/bookmarks/BookmarkedCommunityCard'

type TabType = 'post' | 'exchange' | 'internship' | 'community'

export default function Bookmarks() {
  const { t, i18n } = useTranslation()
  const { bookmarks, loading, error, fetchBookmarks } = useBookmarkStore()
  const [activeTab, setActiveTab] = useState<TabType>('post')

  useEffect(() => {
    console.log('🎬 [Bookmarks] 组件挂载')
    fetchBookmarks()
  }, [])

  // 🔥 关键修复：确保 bookmarks 是数组
  const safeBookmarks = Array.isArray(bookmarks) ? bookmarks : []

  console.log('📊 [Bookmarks] 当前状态:', {
    bookmarksCount: safeBookmarks.length,
    loading,
    error,
    isArray: Array.isArray(bookmarks)
  })

  // 按类型分组 - 使用安全的数组
  const postBookmarks = safeBookmarks.filter(b => b.content_type === 'post')
  const exchangeBookmarks = safeBookmarks.filter(b => b.content_type === 'exchange')
  const internshipBookmarks = safeBookmarks.filter(b => b.content_type === 'internship')
  const communityBookmarks = safeBookmarks.filter(b => b.content_type === 'community')

  const tabs = [
    { key: 'post' as TabType, label: t('bookmarks.tabs.post'), count: postBookmarks.length },
    { key: 'exchange' as TabType, label: t('bookmarks.tabs.exchange'), count: exchangeBookmarks.length },
    { key: 'internship' as TabType, label: t('bookmarks.tabs.internship'), count: internshipBookmarks.length },
    { key: 'community' as TabType, label: t('bookmarks.tabs.community'), count: communityBookmarks.length },
  ]

  const getCurrentBookmarks = () => {
    switch (activeTab) {
      case 'post':
        return postBookmarks
      case 'exchange':
        return exchangeBookmarks
      case 'internship':
        return internshipBookmarks
      case 'community':
        return communityBookmarks
    }
  }

  const totalCount = safeBookmarks.length

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-[32px] font-bold leading-tight text-gray-900">{t('bookmarks.title')}</h1>
        <p className="mt-2 text-base text-gray-600">
          {t('bookmarks.totalCount', { count: totalCount })}
        </p>
      </div>

      {/* Tab Switcher */}
      <div className="flex items-center gap-0 border-b">
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`
              px-4 py-3 text-sm font-medium transition-colors relative
              ${activeTab === tab.key ? 'text-primary' : 'text-gray-600 hover:text-gray-900'}
            `}
          >
            {t('bookmarks.tabCount', { label: tab.label, count: tab.count })}
            {activeTab === tab.key && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      <div>
        {loading && (
          <div className="text-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-500">{t('bookmarks.loading')}</p>
          </div>
        )}

        {error && (
          <div className="text-center py-20">
            <p className="text-red-500 mb-4">{error}</p>
            <button
              onClick={() => fetchBookmarks()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              {t('bookmarks.retry')}
            </button>
          </div>
        )}

        {!loading && !error && getCurrentBookmarks().length === 0 && (
          <div className="text-center py-20">
            <p className="text-gray-500 mb-2">{t('bookmarks.empty')}</p>
            <p className="text-sm text-gray-400">{t('bookmarks.emptyHint')}</p>
          </div>
        )}

        {!loading && !error && getCurrentBookmarks().length > 0 && (
          <div
            className={
              activeTab === 'exchange' || activeTab === 'community'
                ? 'grid grid-cols-2 gap-6' // 交换项目和社区：2列
                : 'space-y-4' // 帖子和实习：单列
            }
          >
            {getCurrentBookmarks().map(bookmark => {
              // 确保 item 存在
              if (!bookmark.item) {
                return null
              }

              return (
                <div key={bookmark.id}>
                  {activeTab === 'post' && (
                    <div className="relative">
                      <PostCard post={bookmark.item} />
                      {/* 在 PostCard 上层显示收藏时间 */}
                      <div className="mt-2 text-xs text-gray-400 px-4">
                        {t('bookmarks.bookmarkedOn', { date: new Date(bookmark.created_at).toLocaleDateString(i18n.language === 'en' ? 'en-US' : 'zh-CN') })}
                      </div>
                    </div>
                  )}
                  {activeTab === 'exchange' && (
                    <BookmarkedExchangeCard
                      program={bookmark.item}
                      bookmarkId={bookmark.id}
                      bookmarkedAt={bookmark.created_at}
                    />
                  )}
                  {activeTab === 'internship' && (
                    <BookmarkedInternshipCard
                      internship={bookmark.item}
                      bookmarkId={bookmark.id}
                      bookmarkedAt={bookmark.created_at}
                    />
                  )}
                  {activeTab === 'community' && (
                    <BookmarkedCommunityCard
                      community={bookmark.item}
                      bookmarkId={bookmark.id}
                      bookmarkedAt={bookmark.created_at}
                    />
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
