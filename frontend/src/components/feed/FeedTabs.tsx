import { Filter } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'

interface FeedTabsProps {
  activeTab: string
  onTabChange: (tab: string) => void
}

const tabs = [
  { id: 'hot', labelKey: 'feed.tabs.hot' },
  { id: 'new', labelKey: 'feed.tabs.new' },
  { id: 'follow', labelKey: 'feed.tabs.follow' },
]

export default function FeedTabs({ activeTab, onTabChange }: FeedTabsProps) {
  const { t } = useTranslation()
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
            {t(tab.labelKey)}
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
        <span className="text-sm">{t('feed.tabs.autoTranslate')}</span>
      </Button>
    </div>
  )
}

