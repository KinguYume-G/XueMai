import { type FormEvent, useCallback, useEffect, useState } from 'react'
import { Briefcase, Clock, DollarSign, MapPin, Plus, Rocket, Search } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { parseApiError } from '@/lib/api/error'
import { opportunitiesApi } from '@/services/api/opportunities'
import type { Internship, Startup } from '@/types/api'

type OpportunityTab = 'internships' | 'startups'

const internshipTypeLabels: Record<string, string> = {
  full_time: '全职',
  part_time: '兼职',
  internship: '实习',
  remote: '远程',
}

export default function Opportunities() {
  const navigate = useNavigate()
  const [tab, setTab] = useState<OpportunityTab>('internships')
  const [internships, setInternships] = useState<Internship[]>([])
  const [startups, setStartups] = useState<Startup[]>([])
  const [type, setType] = useState('')
  const [draft, setDraft] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      if (tab === 'internships') {
        const response = await opportunitiesApi.getInternships({
          limit: 100,
          type: type || undefined,
          search: search || undefined,
        })
        setInternships(response.data)
      } else {
        const response = await opportunitiesApi.getStartups({
          limit: 100,
          search: search || undefined,
        })
        setStartups(response.data)
      }
    } catch (reason) {
      setError(parseApiError(reason))
    } finally {
      setLoading(false)
    }
  }, [search, tab, type])

  useEffect(() => { void load() }, [load])

  const submitSearch = (event: FormEvent) => {
    event.preventDefault()
    setSearch(draft.trim())
  }

  const empty = tab === 'internships' ? internships.length === 0 : startups.length === 0

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">实习与创业机会</h1>
          <p className="mt-2 text-gray-600">所有内容直接来自当前机会数据库。</p>
        </div>
        <Button onClick={() => navigate('/create/job')} className="gap-2"><Plus className="h-4 w-4" />发布机会</Button>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 border-b pb-3">
        <div className="flex gap-2">
          <Button variant={tab === 'internships' ? 'default' : 'ghost'} onClick={() => setTab('internships')} className="gap-2"><Briefcase className="h-4 w-4" />实习与职位</Button>
          <Button variant={tab === 'startups' ? 'default' : 'ghost'} onClick={() => setTab('startups')} className="gap-2"><Rocket className="h-4 w-4" />创业项目</Button>
        </div>
        <form onSubmit={submitSearch} className="flex w-full gap-2 sm:w-auto">
          {tab === 'internships' && (
            <select value={type} onChange={(event) => setType(event.target.value)} className="h-10 rounded-md border bg-white px-3 text-sm">
              <option value="">全部类型</option>
              <option value="internship">实习</option>
              <option value="full_time">全职</option>
              <option value="part_time">兼职</option>
              <option value="remote">远程</option>
            </select>
          )}
          <div className="relative min-w-64 flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <Input value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="搜索职位、公司或项目" className="pl-9" />
          </div>
          <Button type="submit" variant="outline">搜索</Button>
        </form>
      </div>

      {loading ? (
        <Card><CardContent className="p-10 text-center text-gray-500">正在加载机会…</CardContent></Card>
      ) : error ? (
        <Card><CardContent className="space-y-3 p-10 text-center text-red-600"><p>{error}</p><Button variant="outline" onClick={load}>重试</Button></CardContent></Card>
      ) : empty ? (
        <Card><CardContent className="p-10 text-center text-gray-500">没有符合条件的机会</CardContent></Card>
      ) : tab === 'internships' ? (
        <div className="space-y-4">
          {internships.map((item) => (
            <Card key={item.id} className="cursor-pointer transition-shadow hover:shadow-md" onClick={() => navigate(`/internships/${item.id}`)}>
              <CardContent className="p-5">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2"><h2 className="text-lg font-semibold">{item.title}</h2><Badge>{internshipTypeLabels[item.type] ?? item.type}</Badge>{item.remote && <Badge variant="secondary">可远程</Badge>}</div>
                    <p className="mt-1 font-medium text-blue-700">{item.company}</p>
                    <p className="mt-3 line-clamp-2 text-sm leading-6 text-gray-600">{item.description}</p>
                    <div className="mt-4 flex flex-wrap gap-4 text-xs text-gray-500">
                      <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" />{item.location}</span>
                      {item.duration && <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" />{item.duration}</span>}
                      {item.salary_range && <span className="flex items-center gap-1"><DollarSign className="h-3.5 w-3.5" />{item.salary_range}</span>}
                    </div>
                  </div>
                  <div className="text-right text-xs text-gray-500"><div>{item.applicants_count ?? 0} 人申请</div><div className="mt-1">发布于 {item.posted_days ?? 0} 天前</div></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {startups.map((item) => (
            <Card key={item.id} className="cursor-pointer transition-shadow hover:shadow-md" onClick={() => navigate(`/startups/${item.id}`)}>
              <CardContent className="flex min-h-64 flex-col p-5">
                <div className="flex items-start justify-between gap-3"><div><h2 className="text-lg font-semibold">{item.title}</h2><p className="mt-1 text-sm font-medium text-purple-700">{item.org_name}</p></div><Rocket className="h-6 w-6 text-purple-600" /></div>
                <p className="mt-4 line-clamp-3 flex-1 text-sm leading-6 text-gray-600">{item.description_short || item.description}</p>
                {item.tags.length > 0 && <div className="mt-3 flex flex-wrap gap-2">{item.tags.map((tag) => <Badge key={tag} variant="secondary">{tag}</Badge>)}</div>}
                <div className="mt-4 flex items-center justify-between text-xs text-gray-500"><span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" />{[item.city, item.country].filter(Boolean).join(', ')}</span><span>{item.followers_count} 人关注</span></div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
