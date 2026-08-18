import { type FormEvent, useState } from 'react'
import { ArrowLeft, Users } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { parseApiError } from '@/lib/api/error'
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
  const navigate = useNavigate()
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

  const updateName = (value: string) => {
    setName(value)
    if (!slugEdited) setSlug(makeSlug(value))
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!name.trim() || !slug) return
    setSubmitting(true)
    setError(null)
    try {
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
    } catch (reason) {
      setError(parseApiError(reason))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <Button variant="ghost" onClick={() => navigate(-1)} className="gap-2"><ArrowLeft className="h-4 w-4" />返回</Button>
      <Card><CardContent className="p-6">
        <h1 className="text-2xl font-bold">创建社区</h1>
        <p className="mt-2 text-sm text-gray-500">创建后会立即写入社区数据库并进入社区详情页。</p>
        <form onSubmit={submit} className="mt-6 space-y-5">
          <label className="block space-y-2"><span className="text-sm font-medium">社区名称</span><Input value={name} onChange={(event) => updateName(event.target.value)} required maxLength={200} /></label>
          <label className="block space-y-2"><span className="text-sm font-medium">链接标识</span><Input value={slug} onChange={(event) => { setSlugEdited(true); setSlug(makeSlug(event.target.value)) }} required pattern="[a-z0-9-]+" placeholder="例如 apu-basketball" /><span className="text-xs text-gray-500">只允许小写英文字母、数字和连字符，且必须唯一。</span></label>
          <label className="block space-y-2"><span className="text-sm font-medium">社区介绍</span><textarea value={description} onChange={(event) => setDescription(event.target.value)} rows={6} className="w-full rounded-md border bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" /></label>
          <label className="block space-y-2"><span className="text-sm font-medium">封面 URL（可选）</span><Input type="url" value={coverUrl} onChange={(event) => setCoverUrl(event.target.value)} /></label>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block space-y-2"><span className="text-sm font-medium">分类</span><select value={category} onChange={(event) => setCategory(event.target.value as CommunityCategory)} className="h-10 w-full rounded-md border bg-white px-3 text-sm"><option value="interest">兴趣爱好</option><option value="city">城市</option><option value="oncampus">校园</option><option value="study_group">学习小组</option></select></label>
            <label className="block space-y-2"><span className="text-sm font-medium">城市（可选）</span><Input value={city} onChange={(event) => setCity(event.target.value)} /></label>
          </div>
          <label className="block space-y-2"><span className="text-sm font-medium">可见范围</span><select value={visibility} onChange={(event) => setVisibility(event.target.value as typeof visibility)} className="h-10 w-full rounded-md border bg-white px-3 text-sm"><option value="public">公开</option><option value="university">同校</option><option value="private">仅自己</option></select></label>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button type="submit" disabled={submitting || !name.trim() || !slug} className="w-full gap-2"><Users className="h-4 w-4" />{submitting ? '创建中…' : '创建社区'}</Button>
        </form>
      </CardContent></Card>
    </div>
  )
}
