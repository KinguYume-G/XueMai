import { type FormEvent, useEffect, useState } from 'react'
import { ArrowLeft, MessageCircle } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import ErrorState from '@/components/common/ErrorState'
import { parseApiError } from '@/lib/api/error'
import { forumsApi, type Forum } from '@/services/api/forums'
import { useAuthStore } from '@/store/authStore'

export default function CreateTopic() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const isEditMode = Boolean(id)
  const currentUser = useAuthStore((state) => state.user)
  const [forums, setForums] = useState<Forum[]>([])
  const [forum, setForum] = useState('')
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [tags, setTags] = useState('')
  const [visibility, setVisibility] = useState<'public' | 'university' | 'private'>('public')
  const [loadingForums, setLoadingForums] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loadingExisting, setLoadingExisting] = useState(isEditMode)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [forbidden, setForbidden] = useState(false)

  useEffect(() => {
    forumsApi.getForums({ limit: 100 })
      .then((response) => {
        setForums(response.data)
        if (!isEditMode && response.data[0]) setForum(String(response.data[0].id))
      })
      .catch((reason) => setError(parseApiError(reason)))
      .finally(() => setLoadingForums(false))
  }, [isEditMode])

  useEffect(() => {
    if (!isEditMode || !id) return
    let active = true
    setLoadingExisting(true)
    forumsApi
      .getTopic(Number(id))
      .then((topic) => {
        if (!active) return
        if (currentUser && topic.author.id !== currentUser.id) {
          setForbidden(true)
          return
        }
        setForum(String(topic.forum))
        setTitle(topic.title)
        setContent(topic.content)
        setTags(topic.tags.map((tag) => tag.name).join(', '))
        setVisibility(topic.visibility)
      })
      .catch((reason) => active && setLoadError(parseApiError(reason)))
      .finally(() => active && setLoadingExisting(false))
    return () => { active = false }
  }, [id, isEditMode, currentUser])

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!forum || !title.trim() || !content.trim()) return
    setSubmitting(true)
    setError(null)
    try {
      const payload = {
        forum: Number(forum),
        title: title.trim(),
        content: content.trim(),
        tag_names: tags.split(',').map((tag) => tag.trim()).filter(Boolean),
        visibility,
        is_published: true,
      }
      if (isEditMode && id) {
        await forumsApi.updateTopic(Number(id), payload)
        navigate(`/forums/topics/${id}`)
      } else {
        await forumsApi.createTopic(payload)
        navigate(`/forums?forum=${forum}`)
      }
    } catch (reason) {
      setError(parseApiError(reason))
    } finally {
      setSubmitting(false)
    }
  }

  if (isEditMode && loadingExisting) {
    return <Card><CardContent className="p-10 text-center text-gray-500">{t('createTopic.loading')}</CardContent></Card>
  }

  if (isEditMode && (loadError || forbidden)) {
    return (
      <Card><CardContent className="p-6">
        <ErrorState message={loadError || t('createTopic.forbidden')} onRetry={loadError ? () => navigate(0) : undefined} />
      </CardContent></Card>
    )
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <Button variant="ghost" onClick={() => navigate(-1)} className="gap-2"><ArrowLeft className="h-4 w-4" />{t('createTopic.back')}</Button>
      <Card><CardContent className="p-6">
        <h1 className="text-2xl font-bold">{isEditMode ? t('createTopic.titleEdit') : t('createTopic.titleCreate')}</h1>
        <form onSubmit={submit} className="mt-6 space-y-5">
          <label className="block space-y-2"><span className="text-sm font-medium">{t('createTopic.forumLabel')}</span><select value={forum} onChange={(event) => setForum(event.target.value)} disabled={loadingForums} required className="h-10 w-full rounded-md border bg-white px-3 text-sm"><option value="">{t('createTopic.forumPlaceholder')}</option>{forums.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
          <label className="block space-y-2"><span className="text-sm font-medium">{t('createTopic.titleLabel')}</span><Input value={title} onChange={(event) => setTitle(event.target.value)} required maxLength={200} /></label>
          <label className="block space-y-2"><span className="text-sm font-medium">{t('createTopic.contentLabel')}</span><textarea value={content} onChange={(event) => setContent(event.target.value)} required rows={10} className="w-full rounded-md border bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" /></label>
          <label className="block space-y-2"><span className="text-sm font-medium">{t('createTopic.tagsLabel')}</span><Input value={tags} onChange={(event) => setTags(event.target.value)} /></label>
          <label className="block space-y-2"><span className="text-sm font-medium">{t('createTopic.visibilityLabel')}</span><select value={visibility} onChange={(event) => setVisibility(event.target.value as typeof visibility)} className="h-10 w-full rounded-md border bg-white px-3 text-sm"><option value="public">{t('common.visibility.public')}</option><option value="university">{t('common.visibility.university')}</option><option value="private">{t('common.visibility.private')}</option></select></label>
          {forums.length === 0 && !loadingForums && <p className="text-sm text-amber-700">{t('createTopic.noForums')}</p>}
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button type="submit" disabled={submitting || !forum || !title.trim() || !content.trim()} className="w-full gap-2"><MessageCircle className="h-4 w-4" />{submitting ? (isEditMode ? t('createTopic.saving') : t('createTopic.publishing')) : (isEditMode ? t('createTopic.saveChanges') : t('createTopic.publish'))}</Button>
        </form>
      </CardContent></Card>
    </div>
  )
}
