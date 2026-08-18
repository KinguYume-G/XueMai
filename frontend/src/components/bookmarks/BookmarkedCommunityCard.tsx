import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Bookmark, Users } from 'lucide-react'
import { useBookmarkStore } from '@/store/useBookmarkStore'
import { format } from 'date-fns'

interface Props {
  community: any
  bookmarkId: number
  bookmarkedAt: string
}

export function BookmarkedCommunityCard({ community, bookmarkId, bookmarkedAt }: Props) {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { removeBookmark } = useBookmarkStore()
  const [showConfirm, setShowConfirm] = useState(false)

  const handleUnbookmark = async () => {
    await removeBookmark(bookmarkId)
    setShowConfirm(false)
  }

  return (
    <>
      <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-5 relative">
        {/* 右上角：收藏按钮 */}
        <button
          onClick={() => setShowConfirm(true)}
          className="absolute top-4 right-4 text-blue-600 hover:text-blue-700"
        >
          <Bookmark className="w-5 h-5 fill-blue-600" />
        </button>

        {/* 顶部：图标 + 名称 */}
        <div className="flex items-start gap-4 mb-3">
          <div className="w-16 h-16 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-3xl flex-shrink-0">
            {community.icon || '🏛️'}
          </div>
          <div className="flex-1">
            <h3
              onClick={() => navigate(`/communities/${community.slug ?? community.id}`)}
              className="text-lg font-semibold text-gray-900 hover:text-blue-600 cursor-pointer mb-1 pr-6"
            >
              {community.name}
            </h3>
            <div className="flex items-center gap-1 text-sm text-gray-600">
              <Users className="w-4 h-4" />
              <span>{t('bookmarks.communityCard.membersCount', { count: community.members_count || community.students_count || 0 })}</span>
            </div>
          </div>
        </div>

        {/* 简介 */}
        {community.description && (
          <p className="text-sm text-gray-600 mb-4 line-clamp-2">
            {community.description}
          </p>
        )}

        {/* 底部 */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <p className="text-xs text-gray-400">
            {t('bookmarks.bookmarkedOn', { date: format(new Date(bookmarkedAt), 'yyyy-MM-dd') })}
          </p>
          <button
            onClick={() => navigate(`/communities/${community.slug ?? community.id}`)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
          >
            {t('bookmarks.communityCard.enterCommunity')}
          </button>
        </div>
      </div>

      {/* 确认对话框 */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm mx-4">
            <h3 className="text-lg font-semibold mb-2">{t('bookmarks.unbookmarkConfirm.title')}</h3>
            <p className="text-sm text-gray-600 mb-6">
              {t('bookmarks.unbookmarkConfirm.description')}
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowConfirm(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                {t('bookmarks.unbookmarkConfirm.cancel')}
              </button>
              <button
                onClick={handleUnbookmark}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                {t('bookmarks.unbookmarkConfirm.confirm')}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
