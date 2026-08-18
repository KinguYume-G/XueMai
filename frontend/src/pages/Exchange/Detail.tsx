import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ArrowLeft, MapPin, Calendar, ExternalLink, Clock, Bookmark } from 'lucide-react'
import { useExchangeStore } from '@/store/useExchangeStore'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import SkeletonCard from '@/components/common/SkeletonCard'
import ErrorState from '@/components/common/ErrorState'

export default function ExchangeDetailPage() {
  const { t, i18n } = useTranslation()
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { currentProgram, loading, error, fetchProgram } = useExchangeStore()

  useEffect(() => {
    if (id) {
      fetchProgram(parseInt(id, 10))
    }
  }, [id, fetchProgram])

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
              message={error || t('exchange.detail.notFound')}
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
        {t('exchange.detail.backToList')}
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
                  <span>{t('exchange.detail.deadlinePrefix', { date: new Date(currentProgram.deadline).toLocaleDateString(i18n.language === 'en' ? 'en-US' : 'zh-CN') })}</span>
                </div>
              )}
            </div>

            {/* University */}
            <div className="bg-secondary/30 rounded-lg px-4 py-2 inline-block">
              <span className="text-sm font-medium">
                {currentProgram.university}
              </span>
            </div>
          </div>
        </CardHeader>

        <Separator />

        <CardContent className="pt-6 space-y-6">
          {/* Description */}
          <div>
            <h2 className="text-lg font-semibold mb-3">{t('exchange.detail.aboutTitle')}</h2>
            <div className="prose prose-sm max-w-none text-muted-foreground whitespace-pre-wrap">
              {currentProgram.description}
            </div>
          </div>

          <Separator />

          {/* Requirements */}
          <div>
            <h2 className="text-lg font-semibold mb-3">{t('exchange.detail.requirementsTitle')}</h2>
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
                {t('exchange.detail.visitWebsite')}
              </Button>
            )}
            <Button variant="outline" className="gap-2">
              <Bookmark className="h-4 w-4" />
              {t('exchange.detail.bookmark')}
            </Button>
          </div>

          {/* Footer Info */}
          <div className="text-xs text-muted-foreground pt-4 border-t">
            <div className="flex items-center justify-between">
              <span>{t('exchange.detail.postedBy', { id: currentProgram.posted_by })}</span>
              <span>
                {t('exchange.detail.postedAt', { date: new Date(currentProgram.created_at).toLocaleDateString(i18n.language === 'en' ? 'en-US' : 'zh-CN') })}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
