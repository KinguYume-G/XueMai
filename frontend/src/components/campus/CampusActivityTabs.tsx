import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface Activity {
    title: string
    description: string
    image: string
    tag: string
}

interface CampusActivityTabsProps {
    activities: {
        life: Activity[]
        food: Activity[]
        study: Activity[]
        nearby: Activity[]
    }
}

type TabKey = 'life' | 'food' | 'study' | 'nearby'

export default function CampusActivityTabs({ activities }: CampusActivityTabsProps) {
    const [activeTab, setActiveTab] = useState<TabKey>('life')

    const tabs = [
        { key: 'life' as TabKey, label: 'Campus Life', icon: '🎓' },
        { key: 'food' as TabKey, label: 'Food & Dining', icon: '🍽️' },
        { key: 'study' as TabKey, label: 'Study Spaces', icon: '📚' },
        { key: 'nearby' as TabKey, label: 'Nearby', icon: '🏙️' },
    ]

    return (
        <div className="px-6 py-16">
            <div className="max-w-7xl mx-auto">
                <h2 className="text-4xl font-bold text-white mb-4 text-center">
                    Explore Campus Life
                </h2>
                <p className="text-gray-300 text-center mb-12 text-lg">
                    Discover what makes APU a vibrant place to learn and grow
                </p>

                {/* Tab Navigation */}
                <div className="flex flex-wrap justify-center gap-3 mb-12">
                    {tabs.map((tab) => (
                        <button
                            key={tab.key}
                            onClick={() => setActiveTab(tab.key)}
                            className={`
                px-6 py-3 rounded-2xl font-semibold text-lg transition-all duration-300
                ${activeTab === tab.key
                                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-xl scale-105'
                                    : 'bg-slate-800/50 text-gray-300 hover:bg-slate-700/50 hover:text-white'
                                }
              `}
                        >
                            <span className="mr-2">{tab.icon}</span>
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Activity Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {activities[activeTab].map((activity, index) => (
                        <Card
                            key={index}
                            className="bg-white rounded-3xl border-0 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 overflow-hidden group"
                        >
                            <div className="relative h-48 overflow-hidden">
                                <img
                                    src={activity.image}
                                    alt={activity.title}
                                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                                />
                                <div className="absolute inset-0 bg-gradient-to-t from-slate-950/60 to-transparent" />
                                <Badge className="absolute top-4 right-4 bg-white/90 text-slate-900 hover:bg-white">
                                    {activity.tag}
                                </Badge>
                            </div>
                            <CardContent className="p-6">
                                <h3 className="text-xl font-bold text-slate-900 mb-2">
                                    {activity.title}
                                </h3>
                                <p className="text-gray-600 text-sm leading-relaxed">
                                    {activity.description}
                                </p>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>
        </div>
    )
}
