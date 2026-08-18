import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Eye, MessageCircle, Pin, CheckCircle2 } from 'lucide-react'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import SkeletonCard from '@/components/common/SkeletonCard'
import ErrorState from '@/components/common/ErrorState'
import { parseApiError } from '@/lib/api/error'
import { forumsApi, type Topic } from '@/services/api/forums'

export default function TopicDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [topic, setTopic] = useState<Topic | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = () => {
    if (!id) return
    setLoading(true)
    setError(null)
    forumsApi
      .getTopic(Number(id))
      .then(setTopic)
      .catch((reason) => setError(parseApiError(reason)))
      .finally(() => setLoading(false))
  }

  useEffect(load, [id])

  if (loading) {
    return (
      <div className="space-y-4">
        <SkeletonCard count={1} />
      </div>
    )
  }

  if (error || !topic) {
    return (
      <div className="space-y-4">
        <Card className="border shadow-sm">
          <CardContent className="p-6">
            <ErrorState message={error || '话题不存在'} onRetry={load} />
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <Button variant="ghost" onClick={() => navigate('/forums')} className="gap-2">
        <ArrowLeft className="h-4 w-4" />
        返回论坛
      </Button>

      <Card className="border shadow-sm">
        <CardContent className="p-6 space-y-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <Badge variant="outline" className="mb-2">{topic.forum_name}</Badge>
              <h1 className="flex flex-wrap items-center gap-2 text-2xl font-bold">
                {topic.is_pinned && <Pin className="h-5 w-5 text-amber-500" />}
                {topic.title}
                {topic.is_solved && <CheckCircle2 className="h-5 w-5 text-green-600" />}
              </h1>
            </div>
          </div>

          <Link to={`/users/${topic.author.id}`} className="flex items-center gap-3">
            <Avatar>
              <AvatarFallback>{topic.author.username.slice(0, 1).toUpperCase()}</AvatarFallback>
            </Avatar>
            <div>
              <div className="font-medium">{topic.author.username}</div>
              <div className="text-xs text-muted-foreground">{new Date(topic.created_at).toLocaleString('zh-CN')}</div>
            </div>
          </Link>

          <div className="whitespace-pre-wrap text-sm text-muted-foreground">{topic.content}</div>

          {topic.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {topic.tags.map((tag) => (
                <Badge key={tag.id} variant="secondary">#{tag.name}</Badge>
              ))}
            </div>
          )}

          <Separator />

          <div className="flex flex-wrap gap-6 text-sm text-muted-foreground">
            <span className="flex items-center gap-2"><Eye className="h-4 w-4" />{topic.views_count}</span>
            <span className="flex items-center gap-2"><MessageCircle className="h-4 w-4" />{topic.replies_count}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
