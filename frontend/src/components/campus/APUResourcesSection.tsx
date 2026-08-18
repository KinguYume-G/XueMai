import { useEffect, useState } from 'react'
import { BookOpen, Utensils, Trophy, CalendarClock, Bell } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { campusApi, type UniversityResource } from '@/services/api/campus'

// This section renders real campus.UniversityResource rows for APU
// (programmes, dining, sports/recreation, admissions, library, research
// facilities — sourced from apu.edu.my). campusApi.getUniversityResources
// previously had no caller anywhere in the app, so the backing data was
// invisible in the UI even once populated; this wires it up.

const CATEGORY_ICON: Record<UniversityResource['category'], React.ReactNode> = {
  course: <BookOpen className="h-5 w-5" />,
  canteen: <Utensils className="h-5 w-5" />,
  club: <Trophy className="h-5 w-5" />,
  event: <CalendarClock className="h-5 w-5" />,
  notice: <Bell className="h-5 w-5" />,
}

export default function APUResourcesSection() {
  const [resources, setResources] = useState<UniversityResource[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    campusApi
      .getUniversityResources('asia-pacific-university')
      .then((response) => {
        if (active) setResources(response.data ?? [])
      })
      .catch(() => active && setResources([]))
      .finally(() => active && setLoading(false))
    return () => {
      active = false
    }
  }, [])

  if (loading || resources.length === 0) return null

  return (
    <div className="px-6 py-16 bg-slate-950">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-2xl font-bold text-white mb-8">Campus Resources</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {resources.map((resource) => (
            <Card key={resource.id} className="bg-slate-900 border border-slate-800">
              <CardContent className="p-5">
                <div className="flex items-center gap-2 text-blue-400 text-xs font-medium uppercase tracking-wide mb-2">
                  {CATEGORY_ICON[resource.category]}
                  {resource.category_display ?? resource.category}
                </div>
                <h3 className="text-white font-semibold mb-2">{resource.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed line-clamp-5">{resource.content}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
