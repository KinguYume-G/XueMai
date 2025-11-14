import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Calendar, DollarSign, TrendingUp, Bookmark } from 'lucide-react'
import { useBookmarkStore } from '@/store/useBookmarkStore'
import { format } from 'date-fns'

const countryFlags: Record<string, string> = {
  SG: '🇸🇬',
  HK: '🇭🇰',
  JP: '🇯🇵',
  AU: '🇦🇺',
  US: '🇺🇸',
  UK: '🇬🇧',
  CA: '🇨🇦',
  CN: '🇨🇳',
}

interface Props {
  program: any
  bookmarkId: number
  bookmarkedAt: string
}

export function BookmarkedExchangeCard({ program, bookmarkId, bookmarkedAt }: Props) {
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
          <p className="text-sm text-gray-600 mb-1">
            {program.country && countryFlags[program.country]} {program.university || program.location}
          </p>
          <h3
            onClick={() => navigate(`/exchange/${program.id}`)}
            className="text-lg font-semibold text-blue-600 hover:text-blue-700 cursor-pointer pr-10"
          >
            {program.title}
          </h3>
        </div>

        {/* 图标信息行 */}
        <div className="space-y-2 text-sm text-gray-600 mb-4">
          {program.deadline && (
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 flex-shrink-0" />
              <span>申请截止: {program.deadline}</span>
            </div>
          )}
          {program.tuition && (
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4 flex-shrink-0" />
              <span>费用: {program.tuition}</span>
            </div>
          )}
          {(program.gpa_min || program.lang_req) && (
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 flex-shrink-0" />
              <span>
                要求: {program.gpa_min && `GPA≥${program.gpa_min}`}
                {program.gpa_min && program.lang_req && ', '}
                {program.lang_req}
              </span>
            </div>
          )}
        </div>

        {/* 底部 */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <p className="text-xs text-gray-400">
            收藏于 {format(new Date(bookmarkedAt), 'yyyy-MM-dd')}
          </p>
          <button
            onClick={() => navigate(`/exchange/${program.id}`)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
          >
            查看详情
          </button>
        </div>
      </div>

      {/* 确认对话框 */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm mx-4">
            <h3 className="text-lg font-semibold mb-2">确定取消收藏？</h3>
            <p className="text-sm text-gray-600 mb-6">
              此操作将从收藏列表中移除该项目。您可以随时重新收藏。
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowConfirm(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleUnbookmark}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                确定
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
