import { useEffect, useMemo, useState, type MouseEvent } from 'react'
import { Bookmark, BookmarkCheck, Calendar, DollarSign, Gem, Home, MapPin, Users } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import ErrorState from '@/components/common/ErrorState'
import SkeletonCard from '@/components/common/SkeletonCard'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { opportunitiesApi, type Startup } from '@/services/api/opportunities'
import type { Internship } from '@/types/api'

type TabType = 'internship' | 'startup'

export default function Opportunities() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<TabType>('internship')
  const [searchInput, setSearchInput] = useState('')
  const [locationFilter, setLocationFilter] = useState('')
  const [remoteOnly, setRemoteOnly] = useState(false)
  const [internships, setInternships] = useState<Internship[]>([])
  const [startups, setStartups] = useState<Startup[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadOpportunities = async () => {
    setLoading(true)
    setError(null)
    try {
      const [internshipResponse, startupResponse] = await Promise.all([
        opportunitiesApi.getInternships({ search: searchInput || undefined }),
        opportunitiesApi.getStartups({ search: searchInput || undefined }),
      ])
      setInternships(internshipResponse.data ?? [])
      setStartups(startupResponse.data ?? [])
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : '机会列表加载失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const timer = window.setTimeout(loadOpportunities, 250)
    return () => window.clearTimeout(timer)
  }, [searchInput])

  const filteredInternships = useMemo(
    () => internships.filter((item) => {
      const locationMatches = !locationFilter
        || item.location?.includes(locationFilter)
        || item.city?.includes(locationFilter)
        || item.country?.includes(locationFilter)
      return locationMatches && (!remoteOnly || item.remote || item.type === 'remote')
    }),
    [internships, locationFilter, remoteOnly],
  )

  const filteredStartups = useMemo(
    () => startups.filter((item) => !locationFilter
      || item.city?.includes(locationFilter)
      || item.country?.includes(locationFilter)),
    [startups, locationFilter],
  )

  const toggleBookmark = async (item: Internship, event: MouseEvent) => {
    event.stopPropagation()
    try {
      const result = await opportunitiesApi.toggleInternshipBookmark(item.id)
      setInternships((current) => current.map((entry) => (
        entry.id === item.id ? { ...entry, bookmarked: result.bookmarked } : entry
      )))
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : '收藏操作失败')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-[32px] font-bold leading-tight text-gray-900">实习 & 创业机会</h1>
          <p className="mt-2 text-base text-gray-600">发现职业发展和创业机遇</p>
        </div>
        <Button onClick={() => navigate('/create/job')}>发布机会</Button>
      </div>

      <div className="flex items-center border-b">
        {(['internship', 'startup'] as const).map((tab) => (
          <button key={tab} onClick={() => setActiveTab(tab)} className={`relative px-6 py-3 text-sm font-medium ${activeTab === tab ? 'text-primary' : 'text-gray-600 hover:text-gray-900'}`}>
            {tab === 'internship' ? '实习机会' : '创业机会'}
            {activeTab === tab && <span className="absolute inset-x-0 bottom-0 h-[3px] bg-primary" />}
          </button>
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Input placeholder={activeTab === 'internship' ? '搜索职位或公司...' : '搜索项目或组织...'} value={searchInput} onChange={(event) => setSearchInput(event.target.value)} className="h-10 min-w-[240px] flex-1" />
        <Input placeholder="按城市或国家筛选" value={locationFilter} onChange={(event) => setLocationFilter(event.target.value)} className="h-10 w-[200px]" />
        {activeTab === 'internship' && (
          <label className="flex cursor-pointer items-center gap-2 text-sm text-gray-700">
            <input type="checkbox" checked={remoteOnly} onChange={(event) => setRemoteOnly(event.target.checked)} className="h-4 w-4 rounded border-gray-300 text-primary" />
            <Home className="h-4 w-4" />仅看远程
          </label>
        )}
      </div>

      {loading && <SkeletonCard count={3} />}
      {!loading && error && <Card><CardContent className="p-6"><ErrorState message={error} onRetry={loadOpportunities} /></CardContent></Card>}

      {!loading && !error && activeTab === 'internship' && (
        <div className="space-y-4">
          {filteredInternships.map((item) => (
            <Card key={item.id} className="cursor-pointer rounded-xl shadow-sm transition-shadow hover:shadow-md" onClick={() => navigate(`/internships/${item.id}`)}>
              <CardContent className="p-5">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <h3 className="text-lg font-semibold">{item.title}</h3>
                    <p className="mt-1 text-sm text-gray-600">{item.company}</p>
                    <div className="mt-3 flex flex-wrap gap-4 text-sm text-gray-600">
                      <span className="flex items-center gap-1"><MapPin className="h-4 w-4" />{item.location || [item.city, item.country].filter(Boolean).join(' · ') || '地点待定'}</span>
                      {item.salary_range && <span className="flex items-center gap-1"><DollarSign className="h-4 w-4" />{item.salary_range}</span>}
                      {(item.remote || item.type === 'remote') && <span className="flex items-center gap-1"><Home className="h-4 w-4" />支持远程</span>}
                    </div>
                    {!!item.skills?.length && <div className="mt-3 flex flex-wrap gap-2">{item.skills.map((skill) => <Badge key={skill} variant="secondary">{skill}</Badge>)}</div>}
                    <p className="mt-3 line-clamp-2 text-sm text-gray-600">{item.description}</p>
                    <div className="mt-4 flex flex-wrap gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1"><Calendar className="h-4 w-4" />发布 {item.posted_days ?? 0} 天</span>
                      <span className="flex items-center gap-1"><Users className="h-4 w-4" />{item.applicants_count ?? 0} 人申请</span>
                    </div>
                  </div>
                  <button className="rounded-lg p-2 hover:bg-gray-100" aria-label={item.bookmarked ? '取消收藏' : '收藏'} onClick={(event) => toggleBookmark(item, event)}>
                    {item.bookmarked ? <BookmarkCheck className="h-5 w-5 fill-primary text-primary" /> : <Bookmark className="h-5 w-5 text-gray-400" />}
                  </button>
                </div>
              </CardContent>
            </Card>
          ))}
          {!filteredInternships.length && <EmptyState text="暂无符合条件的实习机会" />}
        </div>
      )}

      {!loading && !error && activeTab === 'startup' && (
        <div className="space-y-4">
          {filteredStartups.map((item) => (
            <Card key={item.id} className="rounded-xl shadow-sm transition-shadow hover:shadow-md">
              <CardContent className="p-5">
                <h3 className="text-lg font-semibold">{item.title}</h3>
                <p className="mt-1 text-sm text-gray-600">{item.org_name}</p>
                <div className="mt-3 flex flex-wrap gap-4 text-sm text-gray-600">
                  <span className="flex items-center gap-1"><MapPin className="h-4 w-4" />{[item.city, item.country].filter(Boolean).join(' · ') || '地点待定'}</span>
                  {(item.equity_min !== null || item.equity_max !== null) && <span className="flex items-center gap-1"><Gem className="h-4 w-4" />股权 {formatEquity(item.equity_min, item.equity_max)}</span>}
                  <span className="flex items-center gap-1"><Users className="h-4 w-4" />{item.followers_count} 人关注</span>
                </div>
                {!!item.tags?.length && <div className="mt-3 flex flex-wrap gap-2">{item.tags.map((tag) => <Badge key={tag} variant="secondary">{tag}</Badge>)}</div>}
                <p className="mt-3 line-clamp-3 text-sm text-gray-600">{item.description_short || item.description}</p>
                <div className="mt-4 flex items-center justify-between gap-3">
                  <span className="flex items-center gap-1 text-sm text-gray-500"><Calendar className="h-4 w-4" />发布 {item.posted_days} 天</span>
                  {item.contact_url && <Button size="sm" onClick={() => window.open(item.contact_url, '_blank', 'noopener,noreferrer')}>联系团队</Button>}
                </div>
              </CardContent>
            </Card>
          ))}
          {!filteredStartups.length && <EmptyState text="暂无符合条件的创业机会" />}
        </div>
      )}
    </div>
  )
}

function EmptyState({ text }: { text: string }) {
  return <Card><CardContent className="p-10 text-center text-sm text-gray-500">{text}</CardContent></Card>
}

function formatEquity(min: number | null, max: number | null) {
  if (min !== null && max !== null) return `${min}%–${max}%`
  return `${min ?? max ?? 0}%`
}
