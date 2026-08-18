import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, MapPin, ExternalLink, Users, Percent } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import SkeletonCard from '@/components/common/SkeletonCard'
import ErrorState from '@/components/common/ErrorState'
import { parseApiError } from '@/lib/api/error'
import { opportunitiesApi } from '@/services/api/opportunities'
import type { Startup } from '@/types/api'

export default function StartupDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [startup, setStartup] = useState<Startup | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = () => {
    if (!id) return
    setLoading(true)
    setError(null)
    opportunitiesApi
      .getStartup(Number(id))
      .then(setStartup)
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

  if (error || !startup) {
    return (
      <div className="space-y-4">
        <Card className="border shadow-sm">
          <CardContent className="p-6">
            <ErrorState message={error || '创业项目不存在'} onRetry={load} />
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <Button variant="ghost" onClick={() => navigate('/opportunities')} className="gap-2">
        <ArrowLeft className="h-4 w-4" />
        返回列表
      </Button>

      <Card className="border shadow-sm">
        <CardHeader className="pb-6">
          <div className="space-y-4">
            <div className="flex items-start justify-between gap-4">
              <h1 className="text-3xl font-bold">{startup.title}</h1>
              <Badge variant="default" className="shrink-0">{startup.org_name}</Badge>
            </div>

            <div className="flex flex-wrap gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                <span>{[startup.city, startup.country].filter(Boolean).join(', ')}</span>
              </div>
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4" />
                <span>{startup.followers_count} 位关注者</span>
              </div>
              {(startup.equity_min || startup.equity_max) && (
                <div className="flex items-center gap-2">
                  <Percent className="h-4 w-4" />
                  <span>股权 {startup.equity_min ?? '?'}% - {startup.equity_max ?? '?'}%</span>
                </div>
              )}
            </div>

            {startup.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {startup.tags.map((tag) => (
                  <Badge key={tag} variant="secondary">#{tag}</Badge>
                ))}
              </div>
            )}
          </div>
        </CardHeader>

        <Separator />

        <CardContent className="pt-6 space-y-6">
          <div>
            <h2 className="text-lg font-semibold mb-3">项目介绍</h2>
            <div className="prose prose-sm max-w-none text-muted-foreground whitespace-pre-wrap">
              {startup.description}
            </div>
          </div>

          <Separator />

          <div className="flex gap-3">
            {startup.contact_url && (
              <Button onClick={() => window.open(startup.contact_url, '_blank')} className="gap-2">
                <ExternalLink className="h-4 w-4" />
                联系团队
              </Button>
            )}
          </div>

          <div className="text-xs text-muted-foreground pt-4 border-t">
            <div className="flex items-center justify-between">
              <span>发布者：{startup.posted_by_info?.username ?? `用户 #${startup.posted_by}`}</span>
              <span>发布时间：{new Date(startup.created_at).toLocaleDateString('zh-CN')}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
