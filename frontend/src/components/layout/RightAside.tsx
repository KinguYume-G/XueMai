import SchoolZoneCard from './SchoolZoneCard'
import HotTopicsCard from './HotTopicsCard'
import ExchangeRemindersCard from './ExchangeRemindersCard'

/**
 * Right sidebar component with three cards:
 * 1. School Zone Card - School-specific communities
 * 2. Hot Topics Card - Trending discussion topics
 * 3. Exchange Reminders Card - Upcoming exchange program deadlines
 */
export default function RightAside() {
  return (
    <aside className="fixed right-0 top-16 bottom-0 w-80 overflow-y-auto p-6 space-y-4 bg-transparent">
      <SchoolZoneCard />
      <HotTopicsCard />
      <ExchangeRemindersCard />
    </aside>
  )
}
