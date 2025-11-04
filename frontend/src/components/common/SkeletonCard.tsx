import { Card, CardContent, CardHeader } from '@/components/ui/card'

export default function SkeletonCard({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, index) => (
        <Card key={index} className="border shadow-sm">
          <CardHeader className="pb-3">
            <div className="h-6 bg-secondary rounded-md w-3/4 animate-pulse" />
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="h-4 bg-secondary rounded-md w-full animate-pulse" />
            <div className="h-4 bg-secondary rounded-md w-5/6 animate-pulse" />
            <div className="h-4 bg-secondary rounded-md w-4/6 animate-pulse" />
            <div className="flex gap-2 pt-2">
              <div className="h-8 bg-secondary rounded-md w-20 animate-pulse" />
              <div className="h-8 bg-secondary rounded-md w-24 animate-pulse" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
