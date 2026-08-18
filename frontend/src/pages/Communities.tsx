import { type FormEvent, useCallback, useEffect, useState } from 'react'
import { MapPin, Plus, Search, Users } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { parseApiError } from '@/lib/api/error'
import {
  communitiesApi,
  type CommunityCategory,
  type CommunityRecord,
} from '@/services/api/communities'

const categories: Array<{ value: CommunityCategory | 'all'; label: string }> = [
  { value: 'all', label: '全部' },
  { value: 'interest', label: '兴趣爱好' },
  { value: 'city', label: '城市' },
  { value: 'oncampus', label: '校园' },
  { value: 'study_group', label: '学习小组' },
]

const activityPercent = (value: number) =>
  Math.round(Math.max(0, Math.min(value <= 1 ? value * 100 : value, 100)))

export default function Communities() {
  const navigate = useNavigate()
  const [communities, setCommunities] = useState<CommunityRecord[]>([])
  const [category, setCategory] = useState<CommunityCategory | 'all'>('all')
  const [draft, setDraft] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [joining, setJoining] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const loadCommunities = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await communitiesApi.getCommunities({
        limit: 100,
        category: category === 'all' ? undefined : category,
        search: search || undefined,
      })
      setCommunities(response.data)
    } catch (reason) {
      setError(parseApiError(reason))
    } finally {
      setLoading(false)
    }
  }, [category, search])

  useEffect(() => { void loadCommunities() }, [loadCommunities])

  const submitSearch = (event: FormEvent) => {
    event.preventDefault()
    setSearch(draft.trim())
  }

  const toggleJoin = async (community: CommunityRecord) => {
    setJoining(community.slug)
    setError(null)
    try {
      const result = await communitiesApi.toggleJoin(community.slug)
      const joined = result?.joined ?? !community.joined
      setCommunities((previous) => previous.map((item) => item.slug === community.slug
        ? {
            ...item,
            joined,
            members: Math.max(0, item.members + (joined ? 1 : -1)),
          }
        : item))
    } catch (reason) {
      setError(parseApiError(reason))
    } finally {
      setJoining(null)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">社区</h1>
          <p className="mt-2 text-gray-600">发现并加入真实的校园与兴趣社区。</p>
        </div>
        <Button onClick={() => navigate('/communities/create')} className="gap-2">
          <Plus className="h-4 w-4" />创建社区
        </Button>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2">
          {categories.map((item) => (
            <Button key={item.value} size="sm" variant={category === item.value ? 'default' : 'outline'} onClick={() => setCategory(item.value)}>
              {item.label}
            </Button>
          ))}
        </div>
        <form onSubmit={submitSearch} className="flex w-full gap-2 sm:w-auto">
          <div className="relative min-w-64 flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <Input value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="搜索社区" className="pl-9" />
          </div>
          <Button type="submit" variant="outline">搜索</Button>
        </form>
      </div>

      {error && <Card><CardContent className="p-4 text-sm text-red-600">{error}</CardContent></Card>}

      {loading ? (
        <Card><CardContent className="p-10 text-center text-gray-500">正在加载社区…</CardContent></Card>
      ) : communities.length === 0 ? (
        <Card><CardContent className="p-10 text-center text-gray-500">没有符合条件的社区</CardContent></Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {communities.map((community) => (
            <Card key={community.id} className="overflow-hidden transition-shadow hover:shadow-md">
              {community.cover_url && (
                <button type="button" className="block h-32 w-full" onClick={() => navigate(`/communities/${community.slug}`)}>
                  <img src={community.cover_url} alt="" className="h-full w-full object-cover" />
                </button>
              )}
              <CardContent className="flex min-h-64 flex-col p-5">
                <div className="flex items-start justify-between gap-3">
                  <button type="button" className="text-left" onClick={() => navigate(`/communities/${community.slug}`)}>
                    <h2 className="text-lg font-semibold hover:text-blue-600">{community.name}</h2>
                  </button>
                  <Badge variant="secondary">{categories.find((item) => item.value === community.category)?.label ?? community.category}</Badge>
                </div>
                <p className="mt-3 line-clamp-3 flex-1 text-sm leading-6 text-gray-600">{community.description || '暂无社区介绍'}</p>
                <div className="mt-4 flex flex-wrap gap-3 text-xs text-gray-500">
                  <span className="flex items-center gap-1"><Users className="h-3.5 w-3.5" />{community.members} 位成员</span>
                  <span>{activityPercent(community.activity_rate)}% 活跃度</span>
                  {community.city && <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" />{community.city}</span>}
                </div>
                <div className="mt-5 flex gap-2">
                  <Button variant="outline" className="flex-1" onClick={() => navigate(`/communities/${community.slug}`)}>查看详情</Button>
                  <Button className="flex-1" variant={community.joined ? 'secondary' : 'default'} disabled={joining === community.slug} onClick={() => toggleJoin(community)}>
                    {joining === community.slug ? '处理中…' : community.joined ? '退出社区' : '加入社区'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
