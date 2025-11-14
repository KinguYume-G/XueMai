import { useNavigate } from 'react-router-dom'
import { Construction } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

interface ComingSoonProps {
  title?: string
  message?: string
}

export default function ComingSoon({ title = '功能开发中', message = '该功能正在开发中，敬请期待' }: ComingSoonProps) {
  const navigate = useNavigate()

  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <Card className="w-full max-w-md">
        <CardContent className="flex flex-col items-center justify-center p-12 text-center">
          <div className="w-20 h-20 rounded-full bg-orange-100 flex items-center justify-center mb-6">
            <Construction className="h-10 w-10 text-orange-500" />
          </div>
          <h1 className="text-2xl font-bold mb-3">{title}</h1>
          <p className="text-gray-600 mb-6">{message}</p>
          <Button
            variant="default"
            onClick={() => navigate('/')}
            className="bg-primary hover:bg-primary/90"
          >
            返回首页
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
