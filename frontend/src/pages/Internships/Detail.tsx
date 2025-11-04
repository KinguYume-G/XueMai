import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, MapPin, Briefcase, ExternalLink, Clock, Bookmark, DollarSign, Wifi } from 'lucide-react'
import { useInternshipStore } from '@/store/useInternshipStore'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import SkeletonCard from '@/components/common/SkeletonCard'
import ErrorState from '@/components/common/ErrorState'

export default function InternshipDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { currentInternship, loading, error, fetchInternship } = useInternshipStore()

  useEffect(() => {
    if (id) {
      fetchInternship(parseInt(id, 10))
    }
  }, [id, fetchInternship])

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      full_time: '全职',
      part_time: '兼职',
      internship: '实习',
      remote: '远程',
    }
    return labels[type] || type
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <SkeletonCard count={1} />
      </div>
    )
  }

  if (error || !currentInternship) {
    return (
      <div className="space-y-4">
        <Card className="border shadow-sm">
          <CardContent className="p-6">
            <ErrorState
              message={error || '实习机会不存在'}
              onRetry={() => id && fetchInternship(parseInt(id, 10))}
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
        onClick={() => navigate('/internships')}
        className="gap-2"
      >
        <ArrowLeft className="h-4 w-4" />
        返回列表
      </Button>

      {/* Main Content */}
      <Card className="border shadow-sm">
        <CardHeader className="pb-6">
          <div className="space-y-4">
            {/* Title and Type */}
            <div className="flex items-start justify-between gap-4">
              <h1 className="text-3xl font-bold">{currentInternship.title}</h1>
              <Badge variant="default" className="shrink-0">
                {getTypeLabel(currentInternship.type)}
              </Badge>
            </div>

            {/* Meta Information */}
            <div className="flex flex-wrap gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Briefcase className="h-4 w-4" />
                <span>{currentInternship.company}</span>
              </div>
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                <span>{currentInternship.location}</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                <span>{currentInternship.duration}</span>
              </div>
              {currentInternship.type === 'remote' && (
                <div className="flex items-center gap-2">
                  <Wifi className="h-4 w-4" />
                  <span>远程工作</span>
                </div>
              )}
              {currentInternship.salary_range && (
                <div className="flex items-center gap-2">
                  <DollarSign className="h-4 w-4" />
                  <span>{currentInternship.salary_range}</span>
                </div>
              )}
            </div>
          </div>
        </CardHeader>

        <Separator />

        <CardContent className="pt-6 space-y-6">
          {/* Description */}
          <div>
            <h2 className="text-lg font-semibold mb-3">职位描述</h2>
            <div className="prose prose-sm max-w-none text-muted-foreground whitespace-pre-wrap">
              {currentInternship.description}
            </div>
          </div>

          <Separator />

          {/* Requirements */}
          <div>
            <h2 className="text-lg font-semibold mb-3">任职要求</h2>
            <div className="prose prose-sm max-w-none text-muted-foreground whitespace-pre-wrap">
              {currentInternship.requirements}
            </div>
          </div>

          <Separator />

          {/* Action Buttons */}
          <div className="flex gap-3">
            {currentInternship.link && (
              <Button
                onClick={() => window.open(currentInternship.link, '_blank')}
                className="gap-2"
              >
                <ExternalLink className="h-4 w-4" />
                申请职位
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
              <span>发布者：{currentInternship.posted_by_username}</span>
              <span>
                发布时间：{new Date(currentInternship.created_at).toLocaleDateString('zh-CN')}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
