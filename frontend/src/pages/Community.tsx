import { useEffect, useState } from 'react'
import { ArrowLeft, Calendar, MapPin, Pencil, Trash2, Users } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import ConfirmDialog from '@/components/common/ConfirmDialog'
import { parseApiError } from '@/lib/api/error'
import { useAuthStore } from '@/store/authStore'
import {
  communitiesApi,
  type CommunityRecord,
} from '@/services/api/communities'

const categoryLabels: Record<string, string> = {
  interest: '兴趣爱好',
  city: '城市',
  oncampus: '校园',
  study_group: '学习小组',
}

export default function Community() {
  const { slug } = useParams<{ slug: string }>()
  const navigate = useNavigate()
  const currentUser = useAuthStore((state) => state.user)
  const [community, setCommunity] = useState<CommunityRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const [joining, setJoining] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  useEffect(() => {
    if (!slug) {
      setError('缺少社区标识')
      setLoading(false)
      return
    }

    let active = true
    setLoading(true)
    setError(null)
    communitiesApi.getCommunity(slug)
      .then((data) => active && setCommunity(data))
      .catch((reason) => active && setError(parseApiError(reason)))
      .finally(() => active && setLoading(false))
    return () => { active = false }
  }, [slug])

  const toggleJoin = async () => {
    if (!community) return
    setJoining(true)
    setError(null)
    try {
      const response = await communitiesApi.toggleJoin(community.slug)
      const joined = response?.joined ?? !community.joined
      setCommunity({
        ...community,
        joined,
        members: Math.max(0, community.members + (joined ? 1 : -1)),
      })
    } catch (reason) {
      setError(parseApiError(reason))
    } finally {
      setJoining(false)
    }
  }

  const isOwner = Boolean(community && currentUser && community.created_by === currentUser.id)

  const handleDelete = async () => {
    if (!community) return
    setDeleting(true)
    setDeleteError(null)
    try {
      await communitiesApi.deleteCommunity(community.slug)
      navigate('/communities')
    } catch (reason) {
      setDeleteError(parseApiError(reason))
      setDeleting(false)
      setShowDeleteConfirm(false)
    }
  }

  if (loading) return <Card><CardContent className="p-10 text-center text-gray-500">正在加载社区…</CardContent></Card>

  if (error || !community) {
    return <Card><CardContent className="space-y-4 p-10 text-center"><p className="text-red-600">{error || '社区不存在'}</p><Button variant="outline" onClick={() => navigate('/communities')}>返回社区列表</Button></CardContent></Card>
  }

  const activity = Math.round(Math.min(100, community.activity_rate <= 1 ? community.activity_rate * 100 : community.activity_rate))

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between gap-2">
        <Button variant="ghost" onClick={() => navigate('/communities')} className="gap-2"><ArrowLeft className="h-4 w-4" />返回社区列表</Button>
        {isOwner && (
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="gap-2" onClick={() => navigate(`/communities/${community.slug}/edit`)}>
              <Pencil className="h-4 w-4" />
              编辑
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="gap-2 text-red-600 hover:text-red-700"
              onClick={() => setShowDeleteConfirm(true)}
            >
              <Trash2 className="h-4 w-4" />
              删除
            </Button>
          </div>
        )}
      </div>

      {deleteError && <p className="text-sm text-red-600">{deleteError}</p>}

      <Card className="overflow-hidden">
        {community.cover_url ? (
          <img src={community.cover_url} alt={community.name} className="h-56 w-full object-cover" />
        ) : (
          <div className="h-40 bg-gradient-to-br from-blue-600 to-cyan-500" />
        )}
        <CardContent className="p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-3xl font-bold text-gray-900">{community.name}</h1>
                <Badge variant="secondary">{categoryLabels[community.category] ?? community.category}</Badge>
              </div>
              <div className="mt-3 flex flex-wrap gap-4 text-sm text-gray-500">
                <span className="flex items-center gap-1"><Users className="h-4 w-4" />{community.members} 位成员</span>
                <span>{activity}% 活跃度</span>
                {community.city && <span className="flex items-center gap-1"><MapPin className="h-4 w-4" />{community.city}</span>}
                <span className="flex items-center gap-1"><Calendar className="h-4 w-4" />创建于 {new Date(community.created_at).toLocaleDateString('zh-CN')}</span>
              </div>
            </div>
            <Button onClick={toggleJoin} disabled={joining} variant={community.joined ? 'secondary' : 'default'}>
              {joining ? '处理中…' : community.joined ? '退出社区' : '加入社区'}
            </Button>
          </div>

          <div className="mt-8 border-t pt-6">
            <h2 className="text-lg font-semibold">社区介绍</h2>
            <p className="mt-3 whitespace-pre-wrap leading-7 text-gray-600">{community.description || '该社区暂未填写介绍。'}</p>
          </div>
        </CardContent>
      </Card>

      {showDeleteConfirm && (
        <ConfirmDialog
          title="确定删除这个社区？"
          description="删除后无法恢复，社区的成员关系和相关内容也会一并移除。"
          confirmLabel="删除"
          confirming={deleting}
          onConfirm={handleDelete}
          onCancel={() => setShowDeleteConfirm(false)}
        />
      )}
    </div>
  )
}
