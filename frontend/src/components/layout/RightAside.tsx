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
    <aside className="fixed bottom-0 right-0 top-16 hidden w-80 space-y-4 overflow-y-auto bg-transparent p-6 xl:block">
      <SchoolZoneCard />
      <HotTopicsCard />
      <ExchangeRemindersCard />
    </aside>
  )
}
