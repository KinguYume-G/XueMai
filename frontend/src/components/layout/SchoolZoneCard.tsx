import { useEffect, useState } from 'react'
import { GraduationCap, ChevronRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { universitiesApi, type UniversitySummary } from '@/services/api/universities'

export default function SchoolZoneCard() {
  const navigate = useNavigate()
  const [schools, setSchools] = useState<UniversitySummary[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    universitiesApi.list()
      .then((items) => setSchools(items.slice(0, 3)))
      .catch(() => setSchools([]))
      .finally(() => setLoading(false))
  }, [])

  const handleSchoolClick = (school: UniversitySummary) => {
    if (school.slug === 'apu' || school.name.toLowerCase().includes('asia pacific')) {
      navigate('/apu')
      return
    }
    navigate(`/search?q=${encodeURIComponent(school.name)}`)
  }

  return (
    <Card className="rounded-xl border shadow-sm">
      <CardHeader className="pb-3 px-4 pt-4">
        <CardTitle className="flex items-center gap-2 text-base font-semibold">
          <GraduationCap className="h-5 w-5 text-primary" />
          学校专区
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-0 px-2 pb-2">
        {loading ? <p className="px-3 py-3 text-sm text-muted-foreground">加载中…</p> : null}
        {!loading && schools.length === 0 ? <p className="px-3 py-3 text-sm text-muted-foreground">暂无学校数据</p> : null}
        {schools.map((school) => (
          <button
            key={school.id}
            onClick={() => handleSchoolClick(school)}
            className="flex w-full cursor-pointer items-center justify-between rounded-lg px-3 py-3 text-sm transition-colors hover:bg-secondary/80"
          >
            <div className="flex items-center gap-2">
              <div className="flex flex-col items-start">
                <span className="font-medium text-foreground">
                  {school.name}
                </span>
                <span className="text-xs text-muted-foreground">
                  {school.city || school.country || '大学专区'}
                </span>
              </div>
            </div>
            <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />
          </button>
        ))}
      </CardContent>
    </Card>
  )
}
