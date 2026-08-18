import { type FormEvent, useState } from 'react'
import { ArrowLeft, Send } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { parseApiError } from '@/lib/api/error'
import { postsApi } from '@/services/api/posts'
import type { Visibility } from '@/types/api'

const parseTags = (value: string) => value.split(',').map((tag) => tag.trim()).filter(Boolean)

export default function CreatePost() {
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [imageUrl, setImageUrl] = useState('')
  const [tags, setTags] = useState('')
  const [visibility, setVisibility] = useState<Visibility>('public')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!body.trim()) return
    setSubmitting(true)
    setError(null)
    try {
      await postsApi.createPost({
        title: title.trim(),
        body: body.trim(),
        image_url: imageUrl.trim() || undefined,
        tag_names: parseTags(tags),
        visibility,
        is_published: true,
      })
      navigate('/')
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
        <h1 className="text-2xl font-bold">发布帖子</h1>
        <p className="mt-2 text-sm text-gray-500">帖子将提交到当前账号并立即进入真实内容流。</p>
        <form onSubmit={submit} className="mt-6 space-y-5">
          <label className="block space-y-2"><span className="text-sm font-medium">标题（可选）</span><Input value={title} onChange={(event) => setTitle(event.target.value)} maxLength={200} /></label>
          <label className="block space-y-2"><span className="text-sm font-medium">内容</span><textarea value={body} onChange={(event) => setBody(event.target.value)} required maxLength={5000} rows={10} className="w-full rounded-md border bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" /></label>
          <label className="block space-y-2"><span className="text-sm font-medium">图片 URL（可选）</span><Input type="url" value={imageUrl} onChange={(event) => setImageUrl(event.target.value)} placeholder="https://…" /></label>
          <label className="block space-y-2"><span className="text-sm font-medium">标签（逗号分隔）</span><Input value={tags} onChange={(event) => setTags(event.target.value)} placeholder="课程, 经验分享" /></label>
          <label className="block space-y-2"><span className="text-sm font-medium">可见范围</span><select value={visibility} onChange={(event) => setVisibility(event.target.value as Visibility)} className="h-10 w-full rounded-md border bg-white px-3 text-sm"><option value="public">公开</option><option value="followers">仅关注者</option><option value="university">同校</option><option value="private">仅自己</option></select></label>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button type="submit" disabled={submitting || !body.trim()} className="w-full gap-2"><Send className="h-4 w-4" />{submitting ? '发布中…' : '发布帖子'}</Button>
        </form>
      </CardContent></Card>
    </div>
  )
}
