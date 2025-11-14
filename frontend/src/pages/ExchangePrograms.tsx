import { useEffect } from 'react'
import { useExchangeStore } from '@/store/useExchangeStore'
import { ExchangeCard } from '@/components/exchange/ExchangeCard'
import { ExchangeFilters } from '@/components/exchange/ExchangeFilters'

export default function ExchangePrograms() {
  const { programs, loading, error, fetchPrograms } = useExchangeStore()

  console.log('🎬 ExchangePrograms 组件渲染')
  console.log('📊 当前状态:', {
    programsCount: programs.length,
    loading,
    error,
    hasFetchPrograms: !!fetchPrograms
  })

  useEffect(() => {
    console.log('🎯 useEffect 触发 - 准备调用 fetchPrograms')
    fetchPrograms()
  }, []) // 空数组，只在组件挂载时执行一次

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* 标题区 */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">交换项目</h1>
          <p className="text-base text-gray-600">探索全球顶尖大学的学习机会</p>
        </div>

        {/* 筛选器 */}
        <ExchangeFilters />

        {/* 内容区 */}
        <div className="mt-6">
          {/* Loading 状态 */}
          {loading && (
            <div className="text-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">加载中...</p>
            </div>
          )}

          {/* Error 状态 */}
          {error && !loading && (
            <div className="text-center py-20">
              <p className="text-red-500 mb-4">{error}</p>
              <button
                onClick={fetchPrograms}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                重试
              </button>
            </div>
          )}

          {/* 空态 */}
          {!loading && !error && programs.length === 0 && (
            <div className="text-center py-20">
              <div className="text-6xl mb-4">📪</div>
              <p className="text-gray-500 mb-4">暂无交换项目，敬请期待</p>
            </div>
          )}

          {/* 卡片网格 - 2 行 2 列布局 */}
          {!loading && !error && programs.length > 0 && (
            <div className="grid grid-cols-2 gap-6">
              {programs.map((program) => (
                <ExchangeCard key={program.id} program={program} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
