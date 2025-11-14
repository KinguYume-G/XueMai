import { GraduationCap, Lock, ChevronRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface School {
  id: string
  name: string
  memberCount: string
  isLocked: boolean
  path?: string
}

const schools: School[] = [
  { id: 'apu', name: 'APU 专区', memberCount: '2.3k 成员', isLocked: false, path: '/schools/apu' },
  { id: 'tsinghua', name: '清华大学专区', memberCount: '1.8k 成员', isLocked: true },
  { id: 'pku', name: '北京大学专区', memberCount: '1.5k 成员', isLocked: true },
]

export default function SchoolZoneCard() {
  const navigate = useNavigate()

  const handleSchoolClick = (school: School) => {
    if (!school.isLocked && school.path) {
      navigate(school.path)
    }
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
        {schools.map((school) => (
          <button
            key={school.id}
            onClick={() => handleSchoolClick(school)}
            disabled={school.isLocked}
            className={`
              flex w-full items-center justify-between rounded-lg px-3 py-3 text-sm
              transition-colors
              ${school.isLocked
                ? 'cursor-not-allowed'
                : 'hover:bg-secondary/80 cursor-pointer'
              }
            `}
          >
            <div className="flex items-center gap-2">
              {school.isLocked && (
                <Lock className="h-4 w-4 text-muted-foreground shrink-0" />
              )}
              <div className="flex flex-col items-start">
                <span className={`font-medium ${school.isLocked ? 'text-muted-foreground' : 'text-foreground'}`}>
                  {school.name}
                </span>
                <span className="text-xs text-muted-foreground">
                  {school.memberCount}
                </span>
              </div>
            </div>
            <ChevronRight
              className={`h-4 w-4 shrink-0 ${
                school.isLocked
                  ? 'text-muted-foreground/50'
                  : 'text-muted-foreground group-hover:text-primary'
              }`}
            />
          </button>
        ))}
      </CardContent>
    </Card>
  )
}
