import { useCallback, useEffect, useState } from 'react'
import { Plus, Users } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { parseApiError } from '@/lib/api/error'
import { communitiesApi, type Community, type CommunityCategory } from '@/services/api/communities'

type CategoryFilter = 'all' | CommunityCategory

const categories: Array<{ key: CategoryFilter; label: string }> = [
  { key: 'all', label: '全部' },
  { key: 'interest', label: '兴趣爱好' },
  { key: 'city', label: '城市同乡' },
  { key: 'oncampus', label: '校内社团' },
  { key: 'study_group', label: '学习小组' },
]

export default function Communities() {
  const navigate = useNavigate()
  const [activeCategory, setActiveCategory] = useState<CategoryFilter>('all')
  const [communities, setCommunities] = useState<Community[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadCommunities = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await communitiesApi.list(
        activeCategory === 'all' ? undefined : { category: activeCategory },
      )
      setCommunities(Array.isArray(data) ? data : data.data || [])
    } catch (reason) {
      setError(parseApiError(reason))
    } finally {
      setLoading(false)
    }
  }, [activeCategory])

  useEffect(() => { loadCommunities() }, [loadCommunities])

  const toggleJoin = async (community: Community) => {
    try {
      const result = await communitiesApi.toggleJoin(community.slug)
      setCommunities((items) => items.map((item) => item.id === community.id
        ? { ...item, joined: result.joined, members: Math.max(0, item.members + (result.joined ? 1 : -1)) }
        : item))
    } catch (reason) {
      setError(parseApiError(reason))
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">社区</h1>
          <p className="mt-2 text-muted-foreground">发现兴趣社群、校园组织和学习小组</p>
        </div>
        <Button className="gap-2" onClick={() => navigate('/create/community')}>
          <Plus className="h-4 w-4" /> 创建社区
        </Button>
      </div>

      <div className="flex border-b">
        {categories.map((category) => (
          <button key={category.key} onClick={() => setActiveCategory(category.key)} className={`relative px-4 py-3 text-sm font-medium ${activeCategory === category.key ? 'text-primary' : 'text-muted-foreground hover:text-foreground'}`}>
            {category.label}
            {activeCategory === category.key && <span className="absolute inset-x-0 bottom-0 h-0.5 bg-primary" />}
          </button>
        ))}
      </div>

      {error && <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">{error}</div>}
      {loading ? (
        <div className="py-16 text-center text-muted-foreground">加载社区中…</div>
      ) : communities.length === 0 ? (
        <div className="py-16 text-center text-muted-foreground">当前分类暂无社区</div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {communities.map((community) => (
            <Card key={community.id} className="overflow-hidden">
              {community.cover_url && <img src={community.cover_url} alt="" className="h-28 w-full object-cover" />}
              <CardContent className="space-y-4 p-5">
                <div>
                  <h2 className="text-lg font-semibold">{community.name}</h2>
                  <p className="mt-2 line-clamp-2 min-h-10 text-sm text-muted-foreground">{community.description || '暂无介绍'}</p>
                </div>
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <span className="flex items-center gap-1"><Users className="h-4 w-4" /> {community.members} 位成员</span>
                  {community.city && <span>{community.city}</span>}
                </div>
                <Button className="w-full" variant={community.joined ? 'outline' : 'default'} onClick={() => toggleJoin(community)}>
                  {community.joined ? '退出社区' : '加入社区'}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
