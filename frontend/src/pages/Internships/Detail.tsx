import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ArrowLeft, MapPin, Briefcase, ExternalLink, Clock, Bookmark, DollarSign, Wifi } from 'lucide-react'
import { useInternshipStore } from '@/store/useInternshipStore'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import SkeletonCard from '@/components/common/SkeletonCard'
import ErrorState from '@/components/common/ErrorState'

export default function InternshipDetailPage() {
  const { t, i18n } = useTranslation()
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { currentInternship, loading, error, fetchInternship } = useInternshipStore()

  useEffect(() => {
    if (id) {
      fetchInternship(parseInt(id, 10))
    }
  }, [id, fetchInternship])

  const getTypeLabel = (type: string) => {
    if (type === 'full_time' || type === 'part_time' || type === 'internship' || type === 'remote') {
      return t(`jobTypes.${type}`)
    }
    return type
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
              message={error || t('internships.detail.notFound')}
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
        {t('internships.detail.backToList')}
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
                  <span>{t('internships.detail.remoteWork')}</span>
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
            <h2 className="text-lg font-semibold mb-3">{t('internships.detail.descriptionTitle')}</h2>
            <div className="prose prose-sm max-w-none text-muted-foreground whitespace-pre-wrap">
              {currentInternship.description}
            </div>
          </div>

          <Separator />

          {/* Requirements */}
          <div>
            <h2 className="text-lg font-semibold mb-3">{t('internships.detail.requirementsTitle')}</h2>
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
                {t('internships.detail.apply')}
              </Button>
            )}
            <Button variant="outline" className="gap-2">
              <Bookmark className="h-4 w-4" />
              {t('internships.detail.bookmark')}
            </Button>
          </div>

          {/* Footer Info */}
          <div className="text-xs text-muted-foreground pt-4 border-t">
            <div className="flex items-center justify-between">
              <span>{t('internships.detail.postedBy', { name: currentInternship.posted_by_username })}</span>
              <span>
                {t('internships.detail.postedAt', { date: new Date(currentInternship.created_at).toLocaleDateString(i18n.language === 'en' ? 'en-US' : 'zh-CN') })}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
