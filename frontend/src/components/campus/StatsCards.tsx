import { Card, CardContent } from '@/components/ui/card'

interface Stat {
    value: string
    label: string
    icon?: React.ReactNode
}

interface StatsCardsProps {
    stats: Stat[]
}

export default function StatsCards({ stats }: StatsCardsProps) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 px-6 py-12">
            {stats.map((stat, index) => (
                <Card
                    key={index}
                    className="bg-white rounded-3xl border-0 shadow-2xl hover:shadow-3xl transition-all duration-300 hover:-translate-y-2"
                >
                    <CardContent className="flex flex-col items-center justify-center p-8 h-[200px]">
                        {stat.icon && (
                            <div className="mb-4">
                                {stat.icon}
                            </div>
                        )}
                        <div className="text-5xl font-bold text-slate-900 mb-3 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                            {stat.value}
                        </div>
                        <div className="text-lg text-gray-600 font-medium text-center">
                            {stat.label}
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    )
}
