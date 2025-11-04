import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { MapPin, Briefcase, ExternalLink, DollarSign, Wifi } from 'lucide-react'
import { useInternshipStore } from '@/store/useInternshipStore'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import FilterBar from '@/components/common/FilterBar'
import SkeletonCard from '@/components/common/SkeletonCard'
import ErrorState from '@/components/common/ErrorState'
import EmptyState from '@/components/common/EmptyState'

export default function InternshipsListPage() {
  const navigate = useNavigate()
  const {
    internships,
    loading,
    error,
    filters,
    totalCount,
    currentPage,
    fetchInternships,
    setFilters,
    setPage,
  } = useInternshipStore()

  const [searchInput, setSearchInput] = useState(filters.search || '')

  useEffect(() => {
    fetchInternships()
  }, [fetchInternships])

  const handleSearchChange = (value: string) => {
    setSearchInput(value)
    const timeoutId = setTimeout(() => {
      setFilters({ search: value })
    }, 500)
    return () => clearTimeout(timeoutId)
  }

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      full_time: '全职',
      part_time: '兼职',
      internship: '实习',
      remote: '远程',
    }
    return labels[type] || type
  }

  const totalPages = Math.ceil(totalCount / (filters.page_size || 10))

  return (
    <div className="space-y-4">
      {/* Page Header */}
      <div className="bg-white rounded-2xl border shadow-sm p-6">
        <div className="flex items-center gap-3">
          <div className="rounded-full bg-primary/10 p-2">
            <Briefcase className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">实习 & 机会</h1>
            <p className="text-sm text-muted-foreground">
              探索优质实习与工作机会
            </p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl border shadow-sm overflow-hidden">
        <FilterBar
          searchPlaceholder="搜索职位、公司..."
          searchValue={searchInput}
          onSearchChange={handleSearchChange}
          filters={[
            {
              label: '国家/地区',
              value: filters.country || '',
              options: [
                { value: '', label: '全部国家' },
                { value: 'Malaysia', label: '马来西亚' },
                { value: 'Singapore', label: '新加坡' },
                { value: 'China', label: '中国' },
                { value: 'United States', label: '美国' },
                { value: 'United Kingdom', label: '英国' },
              ],
              onChange: (value) => setFilters({ country: value }),
            },
            {
              label: '类型',
              value: filters.type || '',
              options: [
                { value: '', label: '全部类型' },
                { value: 'internship', label: '实习' },
                { value: 'full_time', label: '全职' },
                { value: 'part_time', label: '兼职' },
                { value: 'remote', label: '远程' },
              ],
              onChange: (value) => setFilters({ type: value }),
            },
          ]}
        />

        {/* Internships List */}
        <div className="p-6">
          {loading ? (
            <SkeletonCard count={3} />
          ) : error ? (
            <ErrorState message={error} onRetry={fetchInternships} />
          ) : internships.length === 0 ? (
            <EmptyState
              message={
                filters.search || filters.country || filters.type
                  ? '没有找到符合条件的实习机会'
                  : '暂无实习机会，敬请期待'
              }
              icon={<Briefcase className="h-8 w-8 text-muted-foreground" />}
            />
          ) : (
            <div className="space-y-4">
              {internships.map((internship) => (
                <Card
                  key={internship.id}
                  className="border shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => navigate(`/internships/${internship.id}`)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between gap-4">
                      <CardTitle className="text-lg font-semibold line-clamp-2">
                        {internship.title}
                      </CardTitle>
                      <Badge variant="default" className="shrink-0">
                        {getTypeLabel(internship.type)}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Briefcase className="h-4 w-4" />
                        <span>{internship.company}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <MapPin className="h-4 w-4" />
                        <span>{internship.location}</span>
                      </div>
                      {internship.type === 'remote' && (
                        <div className="flex items-center gap-1">
                          <Wifi className="h-4 w-4" />
                          <span>远程</span>
                        </div>
                      )}
                      {internship.salary_range && (
                        <div className="flex items-center gap-1">
                          <DollarSign className="h-4 w-4" />
                          <span>{internship.salary_range}</span>
                        </div>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {internship.description}
                    </p>
                    <div className="flex items-center justify-between pt-2">
                      <div className="text-xs text-muted-foreground">
                        {internship.duration}
                      </div>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation()
                          navigate(`/internships/${internship.id}`)
                        }}
                      >
                        查看详情
                        <ExternalLink className="ml-2 h-3 w-3" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* Pagination */}
          {!loading && !error && internships.length > 0 && totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-6">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(currentPage - 1)}
                disabled={currentPage === 1}
              >
                上一页
              </Button>
              <span className="text-sm text-muted-foreground px-4">
                第 {currentPage} / {totalPages} 页
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                下一页
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
