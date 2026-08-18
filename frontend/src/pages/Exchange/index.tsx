import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { MapPin, Calendar, ExternalLink, Globe2 } from 'lucide-react'
import { useExchangeStore } from '@/store/useExchangeStore'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import FilterBar from '@/components/common/FilterBar'
import SkeletonCard from '@/components/common/SkeletonCard'
import ErrorState from '@/components/common/ErrorState'
import EmptyState from '@/components/common/EmptyState'

export default function ExchangeListPage() {
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const {
    programs,
    loading,
    error,
    filters,
    totalCount,
    currentPage,
    fetchPrograms,
    setFilters,
    setPage,
  } = useExchangeStore()

  const [searchInput, setSearchInput] = useState(filters.search || '')

  useEffect(() => {
    console.log('🎬 组件挂载，获取交换项目列表')
    fetchPrograms()
  }, []) // 空数组，只在组件挂载时执行一次

  const handleSearchChange = (value: string) => {
    setSearchInput(value)
    const timeoutId = setTimeout(() => {
      setFilters({ search: value })
    }, 500)
    return () => clearTimeout(timeoutId)
  }

  const formatDeadline = (deadline?: string) => {
    if (!deadline) return t('exchange.deadline.none')
    const date = new Date(deadline)
    const now = new Date()
    const diffDays = Math.ceil((date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))

    if (diffDays < 0) return t('exchange.deadline.expired')
    if (diffDays === 0) return t('exchange.deadline.today')
    if (diffDays <= 7) return t('exchange.deadline.daysLeft', { count: diffDays })
    return date.toLocaleDateString(i18n.language === 'en' ? 'en-US' : 'zh-CN')
  }

  const totalPages = Math.ceil(totalCount / (filters.limit || 20))

  return (
    <div className="space-y-4">
      {/* Page Header */}
      <div className="bg-white rounded-2xl border shadow-sm p-6">
        <div className="flex items-center gap-3">
          <div className="rounded-full bg-primary/10 p-2">
            <Globe2 className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">{t('exchange.title')}</h1>
            <p className="text-sm text-muted-foreground">
              {t('exchange.subtitle')}
            </p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl border shadow-sm overflow-hidden">
        <FilterBar
          searchPlaceholder={t('exchange.searchPlaceholder')}
          searchValue={searchInput}
          onSearchChange={handleSearchChange}
          filters={[
            {
              label: t('exchange.filterCountryLabel'),
              value: filters.country || '',
              options: [
                { value: '', label: t('exchange.countries.all') },
                { value: 'Singapore', label: t('exchange.countries.Singapore') },
                { value: 'Hong Kong', label: t('exchange.countries.HongKong') },
                { value: 'United States', label: t('exchange.countries.UnitedStates') },
                { value: 'United Kingdom', label: t('exchange.countries.UnitedKingdom') },
                { value: 'Australia', label: t('exchange.countries.Australia') },
                { value: 'Japan', label: t('exchange.countries.Japan') },
              ],
              onChange: (value) => setFilters({ country: value }),
            },
          ]}
        />

        {/* Programs List */}
        <div className="p-6">
          {loading ? (
            <SkeletonCard count={3} />
          ) : error ? (
            <ErrorState message={error} onRetry={fetchPrograms} />
          ) : programs.length === 0 ? (
            <EmptyState
              message={
                filters.search || filters.country
                  ? t('exchange.emptyFiltered')
                  : t('exchange.emptyDefault')
              }
              icon={<Globe2 className="h-8 w-8 text-muted-foreground" />}
            />
          ) : (
            <div className="space-y-4">
              {programs.map((program) => (
                <Card
                  key={program.id}
                  className="border shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => navigate(`/exchange/${program.id}`)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between gap-4">
                      <CardTitle className="text-lg font-semibold line-clamp-2">
                        {program.title}
                      </CardTitle>
                      {program.deadline && (
                        <Badge
                          variant={
                            new Date(program.deadline) < new Date()
                              ? 'secondary'
                              : 'default'
                          }
                          className="shrink-0"
                        >
                          {formatDeadline(program.deadline)}
                        </Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <MapPin className="h-4 w-4" />
                        <span>{program.location}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        <span>{program.duration}</span>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {program.description}
                    </p>
                    <div className="flex items-center justify-between pt-2">
                      <div className="text-xs text-muted-foreground">
                        {program.university}
                      </div>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation()
                          navigate(`/exchange/${program.id}`)
                        }}
                      >
                        {t('exchange.viewDetails')}
                        <ExternalLink className="ml-2 h-3 w-3" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* Pagination */}
          {!loading && !error && programs.length > 0 && totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-6">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(currentPage - 1)}
                disabled={currentPage === 1}
              >
                {t('exchange.prevPage')}
              </Button>
              <span className="text-sm text-muted-foreground px-4">
                {t('exchange.pageIndicator', { current: currentPage, total: totalPages })}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                {t('exchange.nextPage')}
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
