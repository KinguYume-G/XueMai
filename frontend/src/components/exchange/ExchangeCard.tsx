import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Calendar, DollarSign, TrendingUp, Star, Users, Bookmark } from 'lucide-react'
import { useExchangeStore } from '@/store/useExchangeStore'
import type { ExchangeProgram } from '@/types/api'

interface ExchangeCardProps {
  program: ExchangeProgram
}

// 国家旗帜映射
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

// 国家渐变背景色映射
const countryGradients: Record<string, string> = {
  SG: 'from-red-500 to-red-600',      // 新加坡 - 红色
  HK: 'from-purple-500 to-purple-600', // 香港 - 紫色
  JP: 'from-pink-500 to-rose-600',     // 日本 - 粉色
  AU: 'from-amber-500 to-orange-600',  // 澳大利亚 - 琥珀色
  US: 'from-blue-600 to-blue-700',     // 美国 - 蓝色
  UK: 'from-indigo-500 to-indigo-600', // 英国 - 靛蓝色
  CA: 'from-red-600 to-red-700',       // 加拿大 - 深红色
  CN: 'from-red-500 to-yellow-600',    // 中国 - 红黄渐变
}

export function ExchangeCard({ program }: ExchangeCardProps) {
  const navigate = useNavigate()
  const { toggleBookmark } = useExchangeStore()
  const [isBookmarked, setIsBookmarked] = useState(program.bookmarked)
  const [imageError, setImageError] = useState(false)

  const handleBookmarkClick = async (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsBookmarked(!isBookmarked)
    await toggleBookmark(program.id)
  }

  const handleCardClick = () => {
    navigate(`/exchange-programs/${program.id}`)
  }

  const handleDetailsClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    navigate(`/exchange-programs/${program.id}`)
  }

  return (
    <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 overflow-hidden cursor-pointer">
      {/* 封面区 */}
      <div className="relative h-[200px] w-full overflow-hidden" onClick={handleCardClick}>
        {/* 封面图或占位符 */}
        {imageError ? (
          <div className={`w-full h-full flex items-center justify-center bg-gradient-to-br ${countryGradients[program.country || ''] || 'from-gray-400 to-gray-600'}`}>
            <div className="text-center text-white">
              <div className="text-6xl mb-3">{countryFlags[program.country || ''] || '🌐'}</div>
              <div className="text-xl font-bold px-4">{program.university}</div>
            </div>
          </div>
        ) : (
          <img
            src={program.cover_url || 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=800'}
            alt={program.title}
            className="w-full h-full object-cover"
            onError={() => {
              console.error('❌ 图片加载失败 [Program ID:', program.id, ']:', program.cover_url)
              setImageError(true)
            }}
            onLoad={() => {
              console.log('✅ 图片加载成功 [Program ID:', program.id, ']:', program.cover_url)
            }}
          />
        )}

        {/* 左上角：国家旗帜 */}
        <div className="absolute top-3 left-3 w-8 h-8 rounded-full bg-white shadow-md flex items-center justify-center text-lg">
          {countryFlags[program.country || ''] || '🌐'}
        </div>

        {/* 右上角：即将截止标签（仅 is_urgent=true 时显示）*/}
        {program.is_urgent && (
          <div className="absolute top-3 right-12 bg-orange-500 text-white text-xs font-medium px-3 py-1 rounded">
            即将截止
          </div>
        )}

        {/* 右上角：收藏按钮 */}
        <button
          onClick={handleBookmarkClick}
          className="absolute top-3 right-3 w-8 h-8 bg-white rounded-full shadow-md flex items-center justify-center hover:bg-gray-50 transition-colors"
        >
          <Bookmark
            className={`w-4 h-4 ${isBookmarked ? 'fill-blue-600 text-blue-600' : 'text-gray-400'}`}
          />
        </button>
      </div>

      {/* 内容区 */}
      <div className="p-5 space-y-3">
        {/* 行1：国家 + 大学 */}
        <p className="text-sm text-gray-600">
          {program.country} {program.university}
        </p>

        {/* 行2：标题 */}
        <h3
          className="text-lg font-semibold text-blue-600 hover:text-blue-700 cursor-pointer"
          onClick={handleCardClick}
        >
          {program.title}
        </h3>

        {/* 行3：简介（2 行省略）*/}
        <p className="text-sm text-gray-600 line-clamp-2">{program.description}</p>

        {/* 行4-6：图标信息行 */}
        <div className="space-y-1 text-sm text-gray-600">
          {/* 申请截止 */}
          {program.deadline && (
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 flex-shrink-0" />
              <span>申请截止: {program.deadline}</span>
            </div>
          )}

          {/* 费用 */}
          {program.tuition && (
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4 flex-shrink-0" />
              <span>费用: {program.tuition}</span>
            </div>
          )}

          {/* 要求 */}
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

        {/* 行7：底部统计行 */}
        <div className="flex items-center justify-between text-sm text-gray-600 pt-2 border-t border-gray-100">
          <div className="flex items-center gap-1">
            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
            <span>{program.rating_avg}/5</span>
            <span className="text-gray-400">({program.rating_count}人评价)</span>
          </div>
          <div className="flex items-center gap-1">
            <Users className="w-4 h-4" />
            <span>{program.applied_count}人已申请</span>
          </div>
        </div>

        {/* 行8：底部按钮行 */}
        <div className="flex gap-3 pt-2">
          <button
            onClick={handleDetailsClick}
            className="flex-1 bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            查看详情
          </button>
          <button
            onClick={handleBookmarkClick}
            className={`flex-1 py-2 rounded-lg font-medium transition-colors ${
              isBookmarked
                ? 'border border-gray-300 text-gray-600 hover:bg-gray-50'
                : 'border border-gray-300 text-gray-600 hover:bg-gray-50'
            }`}
          >
            {isBookmarked ? '已收藏' : '收藏'}
          </button>
        </div>
      </div>
    </div>
  )
}
