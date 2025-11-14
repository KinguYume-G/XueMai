import { useExchangeStore } from '@/store/useExchangeStore'
import { Globe, GraduationCap, Calendar as CalendarIcon, Search } from 'lucide-react'

export function ExchangeFilters() {
  const { filters, setFilters, resetFilters } = useExchangeStore()

  return (
    <div className="bg-white rounded-xl shadow-sm p-4">
      <div className="flex flex-wrap items-center gap-3">
        {/* 筛选器 1：国家/地区 */}
        <div className="flex items-center gap-2 min-w-[180px]">
          <Globe className="w-4 h-4 text-gray-400" />
          <select
            value={filters.country || ''}
            onChange={(e) => setFilters({ country: e.target.value })}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">全部国家/地区</option>
            <option value="SG">新加坡</option>
            <option value="HK">香港</option>
            <option value="JP">日本</option>
            <option value="AU">澳大利亚</option>
            <option value="US">美国</option>
            <option value="UK">英国</option>
            <option value="CA">加拿大</option>
            <option value="CN">中国</option>
          </select>
        </div>

        {/* 筛选器 2：搜索大学 */}
        <div className="flex items-center gap-2 min-w-[240px]">
          <GraduationCap className="w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={filters.university || ''}
            onChange={(e) => setFilters({ university: e.target.value })}
            placeholder="搜索大学名称..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* 筛选器 3：申请截止 */}
        <div className="flex items-center gap-2 min-w-[180px]">
          <CalendarIcon className="w-4 h-4 text-gray-400" />
          <input
            type="date"
            value={filters.deadline_before || ''}
            onChange={(e) => setFilters({ deadline_before: e.target.value })}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* 筛选器 4：搜索关键词 */}
        <div className="flex items-center gap-2 flex-1 min-w-[200px]">
          <Search className="w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={filters.search || ''}
            onChange={(e) => setFilters({ search: e.target.value })}
            placeholder="搜索项目关键词..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* 重置按钮 */}
        <button
          onClick={resetFilters}
          className="px-4 py-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          重置筛选
        </button>
      </div>
    </div>
  )
}
