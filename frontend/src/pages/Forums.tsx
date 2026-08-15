import { useEffect, useState } from 'react'
import { BookOpen, GraduationCap, MessageCircle, Plus, Users } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { parseApiError } from '@/lib/api/error'
import { forumsApi, type Faculty, type ForumOverview } from '@/services/api/forums'

const emptyOverview: ForumOverview = { faculty_count: 0, major_count: 0, active_posts: 0, active_users: 0 }

export default function Forums() {
  const navigate = useNavigate()
  const [overview, setOverview] = useState(emptyOverview)
  const [faculties, setFaculties] = useState<Faculty[]>([])
  const [hotTopics, setHotTopics] = useState<Array<{ name: string; post_count: number }>>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([forumsApi.getOverview(), forumsApi.getFaculties(), forumsApi.getHotTopics()])
      .then(([overviewData, facultyData, topicData]) => {
        setOverview(overviewData)
        setFaculties(facultyData)
        setHotTopics(topicData)
      })
      .catch((reason) => setError(parseApiError(reason)))
      .finally(() => setLoading(false))
  }, [])

  const stats = [
    { label: '学院', value: overview.faculty_count, icon: GraduationCap },
    { label: '专业', value: overview.major_count, icon: BookOpen },
    { label: '话题', value: overview.active_posts, icon: MessageCircle },
    { label: '活跃作者', value: overview.active_users, icon: Users },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">专业论坛</h1>
          <p className="mt-2 text-muted-foreground">按学院和专业讨论课程、研究与学习经验</p>
        </div>
        <Button className="gap-2" onClick={() => navigate('/create/question')}><Plus className="h-4 w-4" /> 提出问题</Button>
      </div>

      {error && <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">{error}</div>}
      {loading ? <div className="py-16 text-center text-muted-foreground">加载论坛中…</div> : <>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {stats.map(({ label, value, icon: Icon }) => <Card key={label}><CardContent className="flex items-center gap-4 p-5"><div className="rounded-xl bg-primary/10 p-3 text-primary"><Icon className="h-6 w-6" /></div><div><p className="text-2xl font-bold">{value.toLocaleString()}</p><p className="text-sm text-muted-foreground">{label}</p></div></CardContent></Card>)}
        </div>

        <section>
          <h2 className="mb-4 text-xl font-semibold">学院</h2>
          {faculties.length === 0 ? <p className="py-8 text-center text-muted-foreground">暂无学院数据</p> : <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{faculties.map((faculty) => <Card key={faculty.id} className="cursor-pointer transition-shadow hover:shadow-md" onClick={() => navigate(`/forums?faculty=${faculty.slug}`)}><CardContent className="space-y-4 p-5"><div className="flex items-start gap-3">{faculty.icon_url ? <img src={faculty.icon_url} alt="" className="h-12 w-12 rounded-xl object-cover" /> : <div className="rounded-xl bg-primary p-3 text-white"><GraduationCap className="h-6 w-6" /></div>}<div><h3 className="font-semibold">{faculty.name}</h3><p className="mt-1 line-clamp-2 text-sm text-muted-foreground">{faculty.description}</p></div></div><div className="flex gap-4 text-sm text-muted-foreground"><span>{faculty.major_count} 个专业</span><span>{faculty.topic_count} 个话题</span></div>{faculty.hot_tags.length > 0 && <div className="flex flex-wrap gap-2">{faculty.hot_tags.map((tag) => <span key={tag} className="rounded-full bg-muted px-2.5 py-1 text-xs">#{tag}</span>)}</div>}</CardContent></Card>)}</div>}
        </section>

        <section>
          <h2 className="mb-4 text-xl font-semibold">热门标签</h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{hotTopics.map((topic) => <button key={topic.name} onClick={() => navigate(`/forums?search=${encodeURIComponent(topic.name)}`)} className="rounded-xl border bg-card p-4 text-left transition-colors hover:border-primary"><p className="font-medium">#{topic.name}</p><p className="mt-1 text-sm text-muted-foreground">{topic.post_count} 个话题</p></button>)}</div>
        </section>
      </>}
    </div>
  )
}
