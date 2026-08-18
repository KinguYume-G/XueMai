import { type FormEvent, useState } from 'react'
import { ArrowLeft, Briefcase } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { parseApiError } from '@/lib/api/error'
import { opportunitiesApi } from '@/services/api/opportunities'
import type { Internship } from '@/types/api'

export default function CreateJob() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [company, setCompany] = useState('')
  const [description, setDescription] = useState('')
  const [location, setLocation] = useState('')
  const [type, setType] = useState<Internship['type']>('internship')
  const [salaryRange, setSalaryRange] = useState('')
  const [deadline, setDeadline] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!title.trim() || !company.trim() || !description.trim() || !location.trim()) return
    setSubmitting(true)
    setError(null)
    try {
      const internship = await opportunitiesApi.createInternship({
        title: title.trim(),
        company: company.trim(),
        description: description.trim(),
        location: location.trim(),
        type,
        salary_range: salaryRange.trim() || undefined,
        deadline: deadline || undefined,
        is_published: true,
      })
      navigate(`/internships/${internship.id}`)
    } catch (reason) {
      setError(parseApiError(reason))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <Button variant="ghost" onClick={() => navigate(-1)} className="gap-2"><ArrowLeft className="h-4 w-4" />{t('createJob.back')}</Button>
      <Card><CardContent className="p-6">
        <h1 className="text-2xl font-bold">{t('createJob.title')}</h1>
        <p className="mt-2 text-sm text-gray-500">{t('createJob.subtitle')}</p>
        <form onSubmit={submit} className="mt-6 space-y-5">
          <label className="block space-y-2"><span className="text-sm font-medium">{t('createJob.titleLabel')}</span><Input value={title} onChange={(event) => setTitle(event.target.value)} required maxLength={200} /></label>
          <label className="block space-y-2"><span className="text-sm font-medium">{t('createJob.companyLabel')}</span><Input value={company} onChange={(event) => setCompany(event.target.value)} required maxLength={200} /></label>
          <label className="block space-y-2"><span className="text-sm font-medium">{t('createJob.descriptionLabel')}</span><textarea value={description} onChange={(event) => setDescription(event.target.value)} required rows={8} className="w-full rounded-md border bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" /></label>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block space-y-2"><span className="text-sm font-medium">{t('createJob.locationLabel')}</span><Input value={location} onChange={(event) => setLocation(event.target.value)} required placeholder={t('createJob.locationPlaceholder')} /></label>
            <label className="block space-y-2"><span className="text-sm font-medium">{t('createJob.typeLabel')}</span><select value={type} onChange={(event) => setType(event.target.value as Internship['type'])} className="h-10 w-full rounded-md border bg-white px-3 text-sm"><option value="internship">{t('createJob.type.internship')}</option><option value="full_time">{t('createJob.type.full_time')}</option><option value="part_time">{t('createJob.type.part_time')}</option><option value="remote">{t('createJob.type.remote')}</option></select></label>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block space-y-2"><span className="text-sm font-medium">{t('createJob.salaryLabel')}</span><Input value={salaryRange} onChange={(event) => setSalaryRange(event.target.value)} placeholder={t('createJob.salaryPlaceholder')} /></label>
            <label className="block space-y-2"><span className="text-sm font-medium">{t('createJob.deadlineLabel')}</span><Input type="date" value={deadline} onChange={(event) => setDeadline(event.target.value)} /></label>
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button type="submit" disabled={submitting || !title.trim() || !company.trim() || !description.trim() || !location.trim()} className="w-full gap-2"><Briefcase className="h-4 w-4" />{submitting ? t('createJob.publishing') : t('createJob.publish')}</Button>
        </form>
      </CardContent></Card>
    </div>
  )
}
