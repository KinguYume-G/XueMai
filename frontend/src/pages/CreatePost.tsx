import { type FormEvent, useEffect, useState } from 'react'
import { ArrowLeft, Send } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import ErrorState from '@/components/common/ErrorState'
import { parseApiError } from '@/lib/api/error'
import { postsApi } from '@/services/api/posts'
import { useAuthStore } from '@/store/authStore'
import type { Visibility } from '@/types/api'

const parseTags = (value: string) => value.split(',').map((tag) => tag.trim()).filter(Boolean)

export default function CreatePost() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const isEditMode = Boolean(id)
  const currentUser = useAuthStore((state) => state.user)
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [imageUrl, setImageUrl] = useState('')
  const [tags, setTags] = useState('')
  const [visibility, setVisibility] = useState<Visibility>('public')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loadingExisting, setLoadingExisting] = useState(isEditMode)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [forbidden, setForbidden] = useState(false)

  useEffect(() => {
    if (!isEditMode || !id) return
    let active = true
    setLoadingExisting(true)
    postsApi
      .getPost(Number(id))
      .then((post) => {
        if (!active) return
        if (currentUser && post.author.id !== currentUser.id) {
          setForbidden(true)
          return
        }
        setTitle(post.title ?? '')
        setBody(post.body)
        setImageUrl(post.image_url ?? '')
        setTags(post.tags.map((tag) => tag.name).join(', '))
        setVisibility(post.visibility)
      })
      .catch((reason) => active && setLoadError(parseApiError(reason)))
      .finally(() => active && setLoadingExisting(false))
    return () => { active = false }
  }, [id, isEditMode, currentUser])

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!body.trim()) return
    setSubmitting(true)
    setError(null)
    try {
      const payload = {
        title: title.trim(),
        body: body.trim(),
        image_url: imageUrl.trim() || undefined,
        tag_names: parseTags(tags),
        visibility,
        is_published: true,
      }
      if (isEditMode && id) {
        await postsApi.updatePost(Number(id), payload)
        navigate(`/posts/${id}`)
      } else {
        await postsApi.createPost(payload)
        navigate('/')
      }
    } catch (reason) {
      setError(parseApiError(reason))
    } finally {
      setSubmitting(false)
    }
  }

  if (isEditMode && loadingExisting) {
    return <Card><CardContent className="p-10 text-center text-gray-500">{t('createPost.loading')}</CardContent></Card>
  }

  if (isEditMode && (loadError || forbidden)) {
    return (
      <Card><CardContent className="p-6">
        <ErrorState message={loadError || t('createPost.forbidden')} onRetry={loadError ? () => navigate(0) : undefined} />
      </CardContent></Card>
    )
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <Button variant="ghost" onClick={() => navigate(-1)} className="gap-2"><ArrowLeft className="h-4 w-4" />{t('createPost.back')}</Button>
      <Card><CardContent className="p-6">
        <h1 className="text-2xl font-bold">{isEditMode ? t('createPost.titleEdit') : t('createPost.titleCreate')}</h1>
        <p className="mt-2 text-sm text-gray-500">{isEditMode ? t('createPost.subtitleEdit') : t('createPost.subtitleCreate')}</p>
        <form onSubmit={submit} className="mt-6 space-y-5">
          <label className="block space-y-2"><span className="text-sm font-medium">{t('createPost.titleLabel')}</span><Input value={title} onChange={(event) => setTitle(event.target.value)} maxLength={200} /></label>
          <label className="block space-y-2"><span className="text-sm font-medium">{t('createPost.contentLabel')}</span><textarea value={body} onChange={(event) => setBody(event.target.value)} required maxLength={5000} rows={10} className="w-full rounded-md border bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" /></label>
          <label className="block space-y-2"><span className="text-sm font-medium">{t('createPost.imageUrlLabel')}</span><Input type="url" value={imageUrl} onChange={(event) => setImageUrl(event.target.value)} placeholder="https://…" /></label>
          <label className="block space-y-2"><span className="text-sm font-medium">{t('createPost.tagsLabel')}</span><Input value={tags} onChange={(event) => setTags(event.target.value)} placeholder={t('createPost.tagsPlaceholder')} /></label>
          <label className="block space-y-2"><span className="text-sm font-medium">{t('createPost.visibilityLabel')}</span><select value={visibility} onChange={(event) => setVisibility(event.target.value as Visibility)} className="h-10 w-full rounded-md border bg-white px-3 text-sm"><option value="public">{t('common.visibility.public')}</option><option value="followers">{t('common.visibility.followers')}</option><option value="university">{t('common.visibility.university')}</option><option value="private">{t('common.visibility.private')}</option></select></label>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button type="submit" disabled={submitting || !body.trim()} className="w-full gap-2"><Send className="h-4 w-4" />{submitting ? (isEditMode ? t('createPost.saving') : t('createPost.publishing')) : (isEditMode ? t('createPost.saveChanges') : t('createPost.publish'))}</Button>
        </form>
      </CardContent></Card>
    </div>
  )
}
