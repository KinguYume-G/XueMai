import { Filter } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface FeedTabsProps {
  activeTab: string
  onTabChange: (tab: string) => void
}

const tabs = [
  { id: 'hot', label: '推荐' },
  { id: 'new', label: '最新' },
  { id: 'follow', label: '关注' },
]

export default function FeedTabs({ activeTab, onTabChange }: FeedTabsProps) {
  return (
    <div className="flex items-center justify-between border-b bg-white">
      <div className="flex">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`relative px-6 py-3.5 text-sm font-medium transition-colors hover:text-foreground ${
              activeTab === tab.id
                ? 'text-foreground'
                : 'text-muted-foreground'
            }`}
          >
            {tab.label}
            {activeTab === tab.id && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
            )}
          </button>
        ))}
      </div>
      
      <Button
        variant="ghost"
        size="sm"
        className="mr-4 gap-2 text-muted-foreground"
      >
        <Filter className="h-4 w-4" />
        <span className="text-sm">自动翻译</span>
      </Button>
    </div>
  )
}

