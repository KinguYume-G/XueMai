import { type FormEvent, type ReactNode, useEffect, useState } from 'react'
import { ArrowRight, Briefcase, FileText, MessageCircle, Search, Users } from 'lucide-react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { parseApiError } from '@/lib/api/error'
import { searchApi, type GlobalSearchResponse } from '@/services/api/search'

const opportunityPath = (kind: string, id: number) => {
  if (kind === 'exchange') return `/exchange/${id}`
  if (kind === 'internship') return `/internships/${id}`
  return `/startups/${id}`
}

export default function SearchResults() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const query = params.get('q')?.trim() ?? ''
  const [draft, setDraft] = useState(query)
  const [data, setData] = useState<GlobalSearchResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setDraft(query)
    if (query.length < 2) {
      setData(null)
      return
    }

    let active = true
    setLoading(true)
    setError(null)
    searchApi
      .search(query)
      .then((response) => active && setData(response))
      .catch((reason) => active && setError(parseApiError(reason)))
      .finally(() => active && setLoading(false))
    return () => {
      active = false
    }
  }, [query])

  const submit = (event: FormEvent) => {
    event.preventDefault()
    const value = draft.trim()
    if (value.length >= 2) navigate(`/search?q=${encodeURIComponent(value)}`)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">全站搜索</h1>
        <p className="mt-2 text-gray-600">查找同学、帖子、论坛话题、社区和机会。</p>
      </div>

      <form onSubmit={submit} className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <Input
            aria-label="搜索关键词"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            className="pl-10"
            placeholder="输入至少两个字符"
          />
        </div>
        <Button type="submit" disabled={draft.trim().length < 2}>搜索</Button>
      </form>

      {loading && <Card><CardContent className="p-8 text-center text-gray-500">正在搜索…</CardContent></Card>}
      {error && <Card><CardContent className="p-8 text-center text-red-600">{error}</CardContent></Card>}
      {!loading && !error && query.length < 2 && (
        <Card><CardContent className="p-8 text-center text-gray-500">请输入至少两个字符开始搜索。</CardContent></Card>
      )}
      {!loading && data && data.total === 0 && (
        <Card><CardContent className="p-8 text-center text-gray-500">没有找到“{query}”相关结果。</CardContent></Card>
      )}

      {data?.results.users?.length ? (
        <ResultSection title="同学" icon={<Users className="h-5 w-5" />}>
          {data.results.users.map((user) => (
            <Link key={user.id} to={`/users/${user.id}`} className="flex items-center gap-3 rounded-lg p-3 hover:bg-gray-50">
              <Avatar><AvatarImage src={user.avatar_url} /><AvatarFallback>{user.username.slice(0, 1).toUpperCase()}</AvatarFallback></Avatar>
              <div className="min-w-0 flex-1">
                <div className="font-medium">{user.username}</div>
                <div className="truncate text-sm text-gray-500">{[user.major, user.university].filter(Boolean).join(' · ') || '学生用户'}</div>
              </div>
              <ArrowRight className="h-4 w-4 text-gray-400" />
            </Link>
          ))}
        </ResultSection>
      ) : null}

      {data?.results.posts?.length ? (
        <ResultSection title="帖子" icon={<FileText className="h-5 w-5" />}>
          {data.results.posts.map((post) => (
            <ResultLink key={post.id} to={`/posts/${post.id}`} title={post.title} subtitle={post.excerpt} />
          ))}
        </ResultSection>
      ) : null}

      {data?.results.topics?.length ? (
        <ResultSection title="论坛话题" icon={<MessageCircle className="h-5 w-5" />}>
          {data.results.topics.map((topic) => (
            <ResultLink key={topic.id} to={`/forums/topics/${topic.id}`} title={topic.title} subtitle={topic.excerpt} />
          ))}
        </ResultSection>
      ) : null}

      {data?.results.communities?.length ? (
        <ResultSection title="社区" icon={<Users className="h-5 w-5" />}>
          {data.results.communities.map((community) => (
            <ResultLink key={community.id} to={`/communities/${community.slug}`} title={community.name} subtitle={`${community.members} 位成员 · ${community.description}`} />
          ))}
        </ResultSection>
      ) : null}

      {data?.results.opportunities?.length ? (
        <ResultSection title="机会" icon={<Briefcase className="h-5 w-5" />}>
          {data.results.opportunities.map((item) => (
            <ResultLink key={`${item.kind}-${item.id}`} to={opportunityPath(item.kind, item.id)} title={item.title} subtitle={item.subtitle} />
          ))}
        </ResultSection>
      ) : null}
    </div>
  )
}

function ResultSection({ title, icon, children }: { title: string; icon: ReactNode; children: ReactNode }) {
  return (
    <Card>
      <CardContent className="p-4">
        <h2 className="mb-2 flex items-center gap-2 text-lg font-semibold">{icon}{title}</h2>
        <div className="divide-y">{children}</div>
      </CardContent>
    </Card>
  )
}

function ResultLink({ to, title, subtitle }: { to: string; title: string; subtitle?: string }) {
  return (
    <Link to={to} className="flex items-center gap-3 rounded-lg p-3 hover:bg-gray-50">
      <div className="min-w-0 flex-1">
        <div className="font-medium">{title}</div>
        {subtitle ? <div className="line-clamp-2 text-sm text-gray-500">{subtitle}</div> : null}
      </div>
      <ArrowRight className="h-4 w-4 shrink-0 text-gray-400" />
    </Link>
  )
}
