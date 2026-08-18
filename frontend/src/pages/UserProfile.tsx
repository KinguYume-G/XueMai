import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, GraduationCap, Link as LinkIcon, Github } from 'lucide-react'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import SkeletonCard from '@/components/common/SkeletonCard'
import ErrorState from '@/components/common/ErrorState'
import { parseApiError } from '@/lib/api/error'
import { usersApi } from '@/services/api/users'
import type { User } from '@/types/api'

export default function UserProfile() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = () => {
    if (!id) return
    setLoading(true)
    setError(null)
    usersApi
      .getUser(Number(id))
      .then(setUser)
      .catch((reason) => setError(parseApiError(reason)))
      .finally(() => setLoading(false))
  }

  useEffect(load, [id])

  if (loading) {
    return (
      <div className="space-y-4">
        <SkeletonCard count={1} />
      </div>
    )
  }

  if (error || !user) {
    return (
      <div className="space-y-4">
        <Card className="border shadow-sm">
          <CardContent className="p-6">
            <ErrorState message={error || '用户不存在'} onRetry={load} />
          </CardContent>
        </Card>
      </div>
    )
  }

  const profile = user.profile

  return (
    <div className="space-y-4">
      <Button variant="ghost" onClick={() => navigate(-1)} className="gap-2">
        <ArrowLeft className="h-4 w-4" />
        返回
      </Button>

      <Card className="border shadow-sm">
        <CardContent className="p-6 space-y-6">
          <div className="flex items-center gap-4">
            <Avatar className="h-16 w-16">
              <AvatarImage src={profile?.avatar_url || user.avatar} />
              <AvatarFallback>{user.username.slice(0, 1).toUpperCase()}</AvatarFallback>
            </Avatar>
            <div>
              <h1 className="text-2xl font-bold">{user.username}</h1>
              {(profile?.major || profile?.university_name) && (
                <p className="text-sm text-muted-foreground">
                  {[profile?.major, profile?.university_name].filter(Boolean).join(' · ')}
                </p>
              )}
            </div>
          </div>

          {(user.bio || profile?.bio) && (
            <p className="whitespace-pre-wrap text-sm text-muted-foreground">{user.bio || profile?.bio}</p>
          )}

          {profile && (
            <>
              <Separator />
              <div className="flex flex-wrap gap-6 text-sm">
                <div><span className="font-semibold">{profile.followers_count}</span> <span className="text-muted-foreground">关注者</span></div>
                <div><span className="font-semibold">{profile.following_count}</span> <span className="text-muted-foreground">正在关注</span></div>
                <div><span className="font-semibold">{profile.posts_count}</span> <span className="text-muted-foreground">帖子</span></div>
              </div>
            </>
          )}

          {(profile?.grade || profile?.school_name) && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <GraduationCap className="h-4 w-4" />
              <span>{[profile?.school_name, profile?.grade].filter(Boolean).join(' · ')}</span>
            </div>
          )}

          {(profile?.website || profile?.github_url || profile?.linkedin_url) && (
            <div className="flex flex-wrap gap-4 text-sm">
              {profile?.website && (
                <a href={profile.website} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-blue-600 hover:underline">
                  <LinkIcon className="h-4 w-4" />网站
                </a>
              )}
              {profile?.github_url && (
                <a href={profile.github_url} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-blue-600 hover:underline">
                  <Github className="h-4 w-4" />GitHub
                </a>
              )}
              {profile?.linkedin_url && (
                <a href={profile.linkedin_url} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-blue-600 hover:underline">
                  <LinkIcon className="h-4 w-4" />LinkedIn
                </a>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
