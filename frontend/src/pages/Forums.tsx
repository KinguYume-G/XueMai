import { type FormEvent, useEffect, useState } from 'react'
import { BookOpen, GraduationCap, MessageCircle, Search, Users } from 'lucide-react'
import { Link, useSearchParams } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button, buttonVariants } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { parseApiError } from '@/lib/api/error'
import {
  forumsApi,
  type Faculty,
  type Forum,
  type ForumOverview,
  type HotTopic,
  type Topic,
} from '@/services/api/forums'

const emptyOverview: ForumOverview = {
  faculty_count: 0,
  major_count: 0,
  active_posts: 0,
  active_users: 0,
}

export default function Forums() {
  const [params, setParams] = useSearchParams()
  const search = params.get('search') ?? ''
  const selectedForum = Number(params.get('forum') ?? 0) || undefined
  const [draft, setDraft] = useState(search)
  const [overview, setOverview] = useState(emptyOverview)
  const [faculties, setFaculties] = useState<Faculty[]>([])
  const [forums, setForums] = useState<Forum[]>([])
  const [hotTopics, setHotTopics] = useState<HotTopic[]>([])
  const [topics, setTopics] = useState<Topic[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    Promise.all([
      forumsApi.getOverview(),
      forumsApi.getFaculties({ limit: 100 }),
      forumsApi.getForums({ limit: 100 }),
      forumsApi.getHotTopics(),
    ])
      .then(([stats, facultyResponse, forumResponse, hot]) => {
        if (!active) return
        setOverview(stats)
        setFaculties(facultyResponse.data)
        setForums(forumResponse.data)
        setHotTopics(hot)
      })
      .catch((reason) => active && setError(parseApiError(reason)))
    return () => { active = false }
  }, [])

  useEffect(() => {
    let active = true
    setLoading(true)
    setError(null)
    forumsApi.getTopics({
      forum: selectedForum,
      search: search || undefined,
      ordering: '-updated_at',
      limit: 50,
    })
      .then((response) => active && setTopics(response.data))
      .catch((reason) => active && setError(parseApiError(reason)))
      .finally(() => active && setLoading(false))
    return () => { active = false }
  }, [search, selectedForum])

  const submitSearch = (event: FormEvent) => {
    event.preventDefault()
    const next = new URLSearchParams(params)
    if (draft.trim()) next.set('search', draft.trim())
    else next.delete('search')
    setParams(next)
  }

  const selectForum = (forumId?: number) => {
    const next = new URLSearchParams(params)
    if (forumId) next.set('forum', String(forumId))
    else next.delete('forum')
    setParams(next)
  }

  const statCards = [
    { label: '学院', value: overview.faculty_count, icon: GraduationCap },
    { label: '专业', value: overview.major_count, icon: BookOpen },
    { label: '话题', value: overview.active_posts, icon: MessageCircle },
    { label: '参与用户', value: overview.active_users, icon: Users },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">专业论坛</h1>
          <p className="mt-2 text-gray-600">浏览真实学院与论坛数据，参与最新讨论。</p>
        </div>
        <Link to="/create/question" className={buttonVariants()}>发布话题</Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {statCards.map(({ label, value, icon: Icon }) => (
          <Card key={label}><CardContent className="flex items-center gap-4 p-5">
            <Icon className="h-8 w-8 text-blue-600" />
            <div><div className="text-2xl font-bold">{value}</div><div className="text-sm text-gray-500">{label}</div></div>
          </CardContent></Card>
        ))}
      </div>

      <section>
        <h2 className="mb-3 text-xl font-semibold">学院</h2>
        {faculties.length === 0 ? (
          <Card><CardContent className="p-6 text-center text-gray-500">暂无学院数据</CardContent></Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {faculties.map((faculty) => (
              <Card key={faculty.id}><CardContent className="p-5">
                <div className="flex items-start gap-3">
                  <div className="rounded-lg bg-blue-50 p-2"><GraduationCap className="h-6 w-6 text-blue-600" /></div>
                  <div className="min-w-0">
                    <h3 className="font-semibold">{faculty.name}</h3>
                    <p className="mt-1 line-clamp-2 text-sm text-gray-500">{faculty.description || '暂无学院介绍'}</p>
                    <p className="mt-3 text-xs text-gray-500">{faculty.major_count} 个专业 · {faculty.topic_count} 个话题</p>
                  </div>
                </div>
              </CardContent></Card>
            ))}
          </div>
        )}
      </section>

      {hotTopics.length > 0 && (
        <section>
          <h2 className="mb-3 text-xl font-semibold">热门标签</h2>
          <div className="flex flex-wrap gap-2">
            {hotTopics.map((topic) => (
              <button
                key={topic.name}
                type="button"
                onClick={() => { setDraft(topic.name); setParams({ search: topic.name }) }}
              >
                <Badge variant="secondary" className="cursor-pointer px-3 py-1.5">#{topic.name} · {topic.post_count}</Badge>
              </button>
            ))}
          </div>
        </section>
      )}

      <section className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap gap-2">
            <Button size="sm" variant={!selectedForum ? 'default' : 'outline'} onClick={() => selectForum()}>全部论坛</Button>
            {forums.map((forum) => (
              <Button key={forum.id} size="sm" variant={selectedForum === forum.id ? 'default' : 'outline'} onClick={() => selectForum(forum.id)}>
                {forum.name} ({forum.topics_count})
              </Button>
            ))}
          </div>
          <form onSubmit={submitSearch} className="flex w-full gap-2 sm:w-auto">
            <div className="relative min-w-64 flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <Input value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="搜索话题" className="pl-9" />
            </div>
            <Button type="submit" variant="outline">搜索</Button>
          </form>
        </div>

        {loading ? (
          <Card><CardContent className="p-8 text-center text-gray-500">正在加载话题…</CardContent></Card>
        ) : error ? (
          <Card><CardContent className="p-8 text-center text-red-600">{error}</CardContent></Card>
        ) : topics.length === 0 ? (
          <Card><CardContent className="p-8 text-center text-gray-500">没有符合条件的话题</CardContent></Card>
        ) : (
          <div className="space-y-3">
            {topics.map((topic) => (
              <Link key={topic.id} to={`/forums/topics/${topic.id}`} className="block">
                <Card className="transition-shadow hover:shadow-md"><CardContent className="p-5">
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        {topic.is_pinned && <Badge>置顶</Badge>}
                        {topic.is_solved && <Badge variant="secondary">已解决</Badge>}
                        <h3 className="font-semibold text-gray-900">{topic.title}</h3>
                      </div>
                      <p className="mt-2 line-clamp-2 text-sm text-gray-600">{topic.content}</p>
                      <p className="mt-3 text-xs text-gray-500">{topic.forum_name} · {topic.author.username} · {new Date(topic.updated_at).toLocaleDateString('zh-CN')}</p>
                    </div>
                    <div className="shrink-0 text-right text-xs text-gray-500">
                      <div>{topic.views_count} 浏览</div><div className="mt-1">{topic.replies_count} 回复</div>
                    </div>
                  </div>
                </CardContent></Card>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
