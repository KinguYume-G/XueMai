import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, MapPin, Calendar, ExternalLink, Clock, Bookmark } from 'lucide-react'
import { useExchangeStore } from '@/store/useExchangeStore'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import SkeletonCard from '@/components/common/SkeletonCard'
import ErrorState from '@/components/common/ErrorState'

export default function ExchangeDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { currentProgram, loading, error, fetchProgram } = useExchangeStore()

  useEffect(() => {
    if (id) {
      fetchProgram(parseInt(id, 10))
    }
  }, [id, fetchProgram])

  const formatDeadline = (deadline?: string) => {
    if (!deadline) return '暂无截止日期'
    const date = new Date(deadline)
    const now = new Date()
    const diffDays = Math.ceil((date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))

    if (diffDays < 0) return '已截止'
    if (diffDays === 0) return '今天截止'
    if (diffDays <= 7) return `${diffDays}天后截止`
    return date.toLocaleDateString('zh-CN')
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <SkeletonCard count={1} />
      </div>
    )
  }

  if (error || !currentProgram) {
    return (
      <div className="space-y-4">
        <Card className="border shadow-sm">
          <CardContent className="p-6">
            <ErrorState
              message={error || '项目不存在'}
              onRetry={() => id && fetchProgram(parseInt(id, 10))}
            />
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Back Button */}
      <Button
        variant="ghost"
        onClick={() => navigate('/exchange')}
        className="gap-2"
      >
        <ArrowLeft className="h-4 w-4" />
        返回列表
      </Button>

      {/* Main Content */}
      <Card className="border shadow-sm">
        <CardHeader className="pb-6">
          <div className="space-y-4">
            {/* Title and Deadline */}
            <div className="flex items-start justify-between gap-4">
              <h1 className="text-3xl font-bold">{currentProgram.title}</h1>
              {currentProgram.deadline && (
                <Badge
                  variant={
                    new Date(currentProgram.deadline) < new Date()
                      ? 'secondary'
                      : 'default'
                  }
                  className="shrink-0"
                >
                  {formatDeadline(currentProgram.deadline)}
                </Badge>
              )}
            </div>

            {/* Meta Information */}
            <div className="flex flex-wrap gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                <span>{currentProgram.location}</span>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                <span>{currentProgram.duration}</span>
              </div>
              {currentProgram.deadline && (
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  <span>截止：{new Date(currentProgram.deadline).toLocaleDateString('zh-CN')}</span>
                </div>
              )}
            </div>

            {/* University */}
            <div className="bg-secondary/30 rounded-lg px-4 py-2 inline-block">
              <span className="text-sm font-medium">
                {currentProgram.host_university_name}
              </span>
            </div>
          </div>
        </CardHeader>

        <Separator />

        <CardContent className="pt-6 space-y-6">
          {/* Description */}
          <div>
            <h2 className="text-lg font-semibold mb-3">项目介绍</h2>
            <div className="prose prose-sm max-w-none text-muted-foreground whitespace-pre-wrap">
              {currentProgram.description}
            </div>
          </div>

          <Separator />

          {/* Requirements */}
          <div>
            <h2 className="text-lg font-semibold mb-3">申请要求</h2>
            <div className="prose prose-sm max-w-none text-muted-foreground whitespace-pre-wrap">
              {currentProgram.requirements}
            </div>
          </div>

          <Separator />

          {/* Action Buttons */}
          <div className="flex gap-3">
            {currentProgram.link && (
              <Button
                onClick={() => window.open(currentProgram.link, '_blank')}
                className="gap-2"
              >
                <ExternalLink className="h-4 w-4" />
                访问官网
              </Button>
            )}
            <Button variant="outline" className="gap-2">
              <Bookmark className="h-4 w-4" />
              收藏
            </Button>
          </div>

          {/* Footer Info */}
          <div className="text-xs text-muted-foreground pt-4 border-t">
            <div className="flex items-center justify-between">
              <span>发布者：{currentProgram.posted_by_username}</span>
              <span>
                发布时间：{new Date(currentProgram.created_at).toLocaleDateString('zh-CN')}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
