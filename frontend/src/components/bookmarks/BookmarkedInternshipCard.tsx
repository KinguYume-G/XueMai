import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { MapPin, DollarSign, Bookmark, Home } from 'lucide-react'
import { useBookmarkStore } from '@/store/useBookmarkStore'
import { format } from 'date-fns'

interface Props {
  internship: any
  bookmarkId: number
  bookmarkedAt: string
}

export function BookmarkedInternshipCard({ internship, bookmarkId, bookmarkedAt }: Props) {
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

        {/* 顶部 */}
        <div className="mb-3">
          <h3
            onClick={() => navigate(`/internships/${internship.id}`)}
            className="text-lg font-semibold text-blue-600 hover:text-blue-700 cursor-pointer mb-2 pr-10"
          >
            {internship.title}
          </h3>
          <p className="text-sm text-blue-600 hover:underline cursor-pointer">
            {internship.company}
          </p>
        </div>

        {/* 图标信息行 */}
        <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-3">
          {internship.location && (
            <div className="flex items-center gap-1">
              <MapPin className="w-4 h-4" />
              <span>{internship.location}</span>
            </div>
          )}
          {internship.salary_range && (
            <div className="flex items-center gap-1">
              <DollarSign className="w-4 h-4" />
              <span>{internship.salary_range}</span>
            </div>
          )}
          {internship.remote && (
            <div className="flex items-center gap-1 text-green-600">
              <Home className="w-4 h-4" />
              <span>{t('bookmarks.internshipCard.remote')}</span>
            </div>
          )}
        </div>

        {/* 技能标签 */}
        {internship.skills && internship.skills.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {internship.skills.slice(0, 5).map((skill: string, index: number) => (
              <span
                key={index}
                className="px-2 py-1 bg-blue-50 text-blue-600 text-xs rounded-full"
              >
                {skill}
              </span>
            ))}
          </div>
        )}

        {/* 底部 */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <p className="text-xs text-gray-400">
            {t('bookmarks.bookmarkedOn', { date: format(new Date(bookmarkedAt), 'yyyy-MM-dd') })}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => navigate(`/internships/${internship.id}`)}
              className="px-3 py-1.5 border border-blue-600 text-blue-600 rounded-lg text-sm hover:bg-blue-50 transition-colors"
            >
              {t('bookmarks.internshipCard.viewDetails')}
            </button>
            {internship.link && (
              <button
                onClick={() => window.open(internship.link, '_blank')}
                className="px-3 py-1.5 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
              >
                {t('bookmarks.internshipCard.applyNow')}
              </button>
            )}
          </div>
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
