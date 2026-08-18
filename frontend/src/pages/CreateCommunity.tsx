import { type FormEvent, useEffect, useState } from 'react'
import { ArrowLeft, Users } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import ErrorState from '@/components/common/ErrorState'
import { parseApiError } from '@/lib/api/error'
import { useAuthStore } from '@/store/authStore'
import {
  communitiesApi,
  type CommunityCategory,
} from '@/services/api/communities'

const makeSlug = (value: string) => value
  .normalize('NFKD')
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-+|-+$/g, '')

export default function CreateCommunity() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { slug: editSlug } = useParams<{ slug: string }>()
  const isEditMode = Boolean(editSlug)
  const currentUser = useAuthStore((state) => state.user)
  const [name, setName] = useState('')
  const [slug, setSlug] = useState('')
  const [slugEdited, setSlugEdited] = useState(false)
  const [description, setDescription] = useState('')
  const [coverUrl, setCoverUrl] = useState('')
  const [category, setCategory] = useState<CommunityCategory>('interest')
  const [city, setCity] = useState('')
  const [visibility, setVisibility] = useState<'public' | 'university' | 'private'>('public')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loadingExisting, setLoadingExisting] = useState(isEditMode)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [forbidden, setForbidden] = useState(false)

  const updateName = (value: string) => {
    setName(value)
    if (!slugEdited) setSlug(makeSlug(value))
  }

  useEffect(() => {
    if (!isEditMode || !editSlug) return
    let active = true
    setLoadingExisting(true)
    communitiesApi
      .getCommunity(editSlug)
      .then((community) => {
        if (!active) return
        if (currentUser && community.created_by !== currentUser.id) {
          setForbidden(true)
          return
        }
        setName(community.name)
        setSlug(community.slug)
        setSlugEdited(true)
        setDescription(community.description ?? '')
        setCoverUrl(community.cover_url ?? '')
        setCategory(community.category)
        setCity(community.city ?? '')
        setVisibility(community.visibility)
      })
      .catch((reason) => active && setLoadError(parseApiError(reason)))
      .finally(() => active && setLoadingExisting(false))
    return () => { active = false }
  }, [editSlug, isEditMode, currentUser])

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!name.trim() || !slug) return
    setSubmitting(true)
    setError(null)
    try {
      if (isEditMode && editSlug) {
        // The slug is the route key for this resource; keep it fixed on edit
        // so the detail page's URL and any existing links stay valid.
        await communitiesApi.updateCommunity(editSlug, {
          name: name.trim(),
          description: description.trim(),
          cover_url: coverUrl.trim() || undefined,
          category,
          city: city.trim() || undefined,
          is_oncampus: category === 'oncampus',
          is_study_group: category === 'study_group',
          visibility,
        })
        navigate(`/communities/${editSlug}`)
      } else {
        const community = await communitiesApi.createCommunity({
          name: name.trim(),
          slug,
          description: description.trim(),
          cover_url: coverUrl.trim() || undefined,
          category,
          city: city.trim() || undefined,
          is_oncampus: category === 'oncampus',
          is_study_group: category === 'study_group',
          visibility,
          is_published: true,
        })
        navigate(`/communities/${community.slug}`)
      }
    } catch (reason) {
      setError(parseApiError(reason))
    } finally {
      setSubmitting(false)
    }
  }

  if (isEditMode && loadingExisting) {
    return <Card><CardContent className="p-10 text-center text-gray-500">{t('createCommunity.loading')}</CardContent></Card>
  }

  if (isEditMode && (loadError || forbidden)) {
    return (
      <Card><CardContent className="p-6">
        <ErrorState message={loadError || t('createCommunity.forbidden')} onRetry={loadError ? () => navigate(0) : undefined} />
      </CardContent></Card>
    )
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <Button variant="ghost" onClick={() => navigate(-1)} className="gap-2"><ArrowLeft className="h-4 w-4" />{t('createCommunity.back')}</Button>
      <Card><CardContent className="p-6">
        <h1 className="text-2xl font-bold">{isEditMode ? t('createCommunity.titleEdit') : t('createCommunity.titleCreate')}</h1>
        <p className="mt-2 text-sm text-gray-500">{isEditMode ? t('createCommunity.subtitleEdit') : t('createCommunity.subtitleCreate')}</p>
        <form onSubmit={submit} className="mt-6 space-y-5">
          <label className="block space-y-2"><span className="text-sm font-medium">{t('createCommunity.nameLabel')}</span><Input value={name} onChange={(event) => updateName(event.target.value)} required maxLength={200} /></label>
          <label className="block space-y-2">
            <span className="text-sm font-medium">{t('createCommunity.slugLabel')}</span>
            <Input
              value={slug}
              onChange={(event) => { setSlugEdited(true); setSlug(makeSlug(event.target.value)) }}
              required
              pattern="[a-z0-9-]+"
              placeholder={t('createCommunity.slugPlaceholder')}
              disabled={isEditMode}
            />
            <span className="text-xs text-gray-500">
              {isEditMode ? t('createCommunity.slugHintEdit') : t('createCommunity.slugHintCreate')}
            </span>
          </label>
          <label className="block space-y-2"><span className="text-sm font-medium">{t('createCommunity.descriptionLabel')}</span><textarea value={description} onChange={(event) => setDescription(event.target.value)} rows={6} className="w-full rounded-md border bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" /></label>
          <label className="block space-y-2"><span className="text-sm font-medium">{t('createCommunity.coverUrlLabel')}</span><Input type="url" value={coverUrl} onChange={(event) => setCoverUrl(event.target.value)} /></label>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block space-y-2"><span className="text-sm font-medium">{t('createCommunity.categoryLabel')}</span><select value={category} onChange={(event) => setCategory(event.target.value as CommunityCategory)} className="h-10 w-full rounded-md border bg-white px-3 text-sm"><option value="interest">{t('communities.categories.interest')}</option><option value="city">{t('communities.categories.city')}</option><option value="oncampus">{t('communities.categories.oncampus')}</option><option value="study_group">{t('communities.categories.study_group')}</option></select></label>
            <label className="block space-y-2"><span className="text-sm font-medium">{t('createCommunity.cityLabel')}</span><Input value={city} onChange={(event) => setCity(event.target.value)} /></label>
          </div>
          <label className="block space-y-2"><span className="text-sm font-medium">{t('createCommunity.visibilityLabel')}</span><select value={visibility} onChange={(event) => setVisibility(event.target.value as typeof visibility)} className="h-10 w-full rounded-md border bg-white px-3 text-sm"><option value="public">{t('common.visibility.public')}</option><option value="university">{t('common.visibility.university')}</option><option value="private">{t('common.visibility.private')}</option></select></label>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button type="submit" disabled={submitting || !name.trim() || !slug} className="w-full gap-2"><Users className="h-4 w-4" />{submitting ? (isEditMode ? t('createCommunity.saving') : t('createCommunity.creating')) : (isEditMode ? t('createCommunity.saveChanges') : t('createCommunity.create'))}</Button>
        </form>
      </CardContent></Card>
    </div>
  )
}
