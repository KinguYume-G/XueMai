import { useEffect, useMemo, useState, type FormEvent, type ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { parseApiError } from '@/lib/api/error'
import { communitiesApi, type CommunityCategory } from '@/services/api/communities'
import { forumsApi, type Forum } from '@/services/api/forums'
import { opportunitiesApi } from '@/services/api/opportunities'
import { postsApi } from '@/services/api/posts'

type CreateKind = 'post' | 'question' | 'community' | 'job'

interface CreateContentProps {
  kind: CreateKind
}

const config = {
  post: { title: '发布帖子', description: '分享校园动态、经验或作品', successPath: '/' },
  question: { title: '提出问题', description: '在专业论坛中发起讨论', successPath: '/forums' },
  community: { title: '创建社区', description: '建立一个新的兴趣或学习社区', successPath: '/communities' },
  job: { title: '发布职位', description: '发布实习、兼职或全职机会', successPath: '/opportunities' },
} satisfies Record<CreateKind, { title: string; description: string; successPath: string }>

const textareaClass = 'min-h-32 w-full resize-y rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring'
const selectClass = 'h-10 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring'

export default function CreateContent({ kind }: CreateContentProps) {
  const navigate = useNavigate()
  const page = config[kind]
  const [values, setValues] = useState<Record<string, string>>({})
  const [forums, setForums] = useState<Forum[]>([])
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (kind !== 'question') return
    forumsApi.getForums().then(setForums).catch((reason) => setError(parseApiError(reason)))
  }, [kind])

  const required = useMemo(() => {
    if (kind === 'post') return ['body']
    if (kind === 'question') return ['forum', 'title', 'content']
    if (kind === 'community') return ['name', 'category']
    return ['title', 'company', 'description', 'location', 'type']
  }, [kind])

  const setValue = (key: string, value: string) => setValues((current) => ({ ...current, [key]: value }))
  const canSubmit = required.every((field) => values[field]?.trim())

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!canSubmit) return
    setSubmitting(true)
    setError(null)

    try {
      if (kind === 'post') {
        await postsApi.createPost({
          title: values.title?.trim() || undefined,
          body: values.body.trim(),
          tag_names: values.tags?.split(',').map((tag) => tag.trim()).filter(Boolean),
          visibility: values.visibility || 'public',
          is_published: true,
        })
      } else if (kind === 'question') {
        await forumsApi.createTopic({
          forum: Number(values.forum),
          title: values.title.trim(),
          content: values.content.trim(),
          tag_names: values.tags?.split(',').map((tag) => tag.trim()).filter(Boolean),
        })
      } else if (kind === 'community') {
        const category = values.category as CommunityCategory
        await communitiesApi.create({
          name: values.name.trim(),
          description: values.description?.trim(),
          category,
          city: values.city?.trim(),
          cover_url: values.cover_url?.trim(),
          is_oncampus: category === 'oncampus',
          is_study_group: category === 'study_group',
        })
      } else {
        await opportunitiesApi.createInternship({
          title: values.title.trim(),
          company: values.company.trim(),
          description: values.description.trim(),
          location: values.location.trim(),
          type: values.type as 'full_time' | 'part_time' | 'internship' | 'remote',
          duration: values.duration?.trim(),
          deadline: values.deadline || undefined,
          requirements: values.requirements?.trim(),
          salary_range: values.salary_range?.trim(),
          link: values.link?.trim(),
          skills: values.skills?.split(',').map((skill) => skill.trim()).filter(Boolean),
          remote: values.type === 'remote',
          visibility: 'public',
          is_published: true,
        })
      }
      navigate(page.successPath)
    } catch (reason) {
      setError(parseApiError(reason))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <Button variant="ghost" className="gap-2" onClick={() => navigate(-1)}>
        <ArrowLeft className="h-4 w-4" /> 返回
      </Button>
      <Card>
        <CardHeader>
          <CardTitle>{page.title}</CardTitle>
          <CardDescription>{page.description}</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-5" onSubmit={handleSubmit}>
            {kind === 'post' && <PostFields values={values} setValue={setValue} />}
            {kind === 'question' && <QuestionFields values={values} setValue={setValue} forums={forums} />}
            {kind === 'community' && <CommunityFields values={values} setValue={setValue} />}
            {kind === 'job' && <JobFields values={values} setValue={setValue} />}
            {error && <p className="text-sm text-destructive">{error}</p>}
            <div className="flex justify-end gap-3 border-t pt-5">
              <Button type="button" variant="outline" onClick={() => navigate(-1)}>取消</Button>
              <Button type="submit" disabled={!canSubmit || submitting}>
                {submitting ? '提交中…' : '发布'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

type FieldsProps = { values: Record<string, string>; setValue: (key: string, value: string) => void }
const Field = ({ label, children }: { label: string; children: ReactNode }) => <label className="block space-y-2"><span className="text-sm font-medium">{label}</span>{children}</label>

function PostFields({ values, setValue }: FieldsProps) {
  return <><Field label="标题（可选）"><Input value={values.title || ''} onChange={(e) => setValue('title', e.target.value)} /></Field><Field label="内容"><textarea className={textareaClass} value={values.body || ''} onChange={(e) => setValue('body', e.target.value)} /></Field><Field label="标签（逗号分隔）"><Input value={values.tags || ''} onChange={(e) => setValue('tags', e.target.value)} /></Field><Field label="可见范围"><select className={selectClass} value={values.visibility || 'public'} onChange={(e) => setValue('visibility', e.target.value)}><option value="public">公开</option><option value="followers">仅关注者</option><option value="university">同校可见</option><option value="private">仅自己</option></select></Field></>
}

function QuestionFields({ values, setValue, forums }: FieldsProps & { forums: Forum[] }) {
  return <><Field label="论坛"><select className={selectClass} value={values.forum || ''} onChange={(e) => setValue('forum', e.target.value)}><option value="">选择论坛</option>{forums.map((forum) => <option key={forum.id} value={forum.id}>{forum.name}</option>)}</select></Field><Field label="问题标题"><Input value={values.title || ''} onChange={(e) => setValue('title', e.target.value)} /></Field><Field label="问题描述"><textarea className={textareaClass} value={values.content || ''} onChange={(e) => setValue('content', e.target.value)} /></Field><Field label="标签（逗号分隔）"><Input value={values.tags || ''} onChange={(e) => setValue('tags', e.target.value)} /></Field></>
}

function CommunityFields({ values, setValue }: FieldsProps) {
  return <><Field label="社区名称"><Input value={values.name || ''} onChange={(e) => setValue('name', e.target.value)} /></Field><Field label="社区类型"><select className={selectClass} value={values.category || ''} onChange={(e) => setValue('category', e.target.value)}><option value="">选择类型</option><option value="interest">兴趣爱好</option><option value="city">城市</option><option value="oncampus">校园</option><option value="study_group">学习小组</option></select></Field><Field label="城市（可选）"><Input value={values.city || ''} onChange={(e) => setValue('city', e.target.value)} /></Field><Field label="社区介绍"><textarea className={textareaClass} value={values.description || ''} onChange={(e) => setValue('description', e.target.value)} /></Field><Field label="封面 URL（可选）"><Input type="url" value={values.cover_url || ''} onChange={(e) => setValue('cover_url', e.target.value)} /></Field></>
}

function JobFields({ values, setValue }: FieldsProps) {
  return <><div className="grid gap-4 sm:grid-cols-2"><Field label="职位名称"><Input value={values.title || ''} onChange={(e) => setValue('title', e.target.value)} /></Field><Field label="公司名称"><Input value={values.company || ''} onChange={(e) => setValue('company', e.target.value)} /></Field><Field label="工作地点"><Input value={values.location || ''} onChange={(e) => setValue('location', e.target.value)} /></Field><Field label="职位类型"><select className={selectClass} value={values.type || ''} onChange={(e) => setValue('type', e.target.value)}><option value="">选择类型</option><option value="internship">实习</option><option value="full_time">全职</option><option value="part_time">兼职</option><option value="remote">远程</option></select></Field><Field label="申请截止日期"><Input type="date" value={values.deadline || ''} onChange={(e) => setValue('deadline', e.target.value)} /></Field><Field label="薪资范围"><Input value={values.salary_range || ''} onChange={(e) => setValue('salary_range', e.target.value)} /></Field></div><Field label="职位描述"><textarea className={textareaClass} value={values.description || ''} onChange={(e) => setValue('description', e.target.value)} /></Field><Field label="职位要求"><textarea className={textareaClass} value={values.requirements || ''} onChange={(e) => setValue('requirements', e.target.value)} /></Field><Field label="技能（逗号分隔）"><Input value={values.skills || ''} onChange={(e) => setValue('skills', e.target.value)} /></Field><Field label="申请链接"><Input type="url" value={values.link || ''} onChange={(e) => setValue('link', e.target.value)} /></Field></>
}
