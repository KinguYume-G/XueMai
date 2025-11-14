import { Search } from 'lucide-react'
import { Input } from '@/components/ui/input'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

export interface FilterOption {
  value: string
  label: string
}

interface FilterBarProps {
  searchPlaceholder?: string
  searchValue?: string
  onSearchChange?: (value: string) => void
  filters?: {
    label: string
    value: string
    options: FilterOption[]
    onChange: (value: string) => void
  }[]
}

export default function FilterBar({
  searchPlaceholder = '搜索...',
  searchValue = '',
  onSearchChange,
  filters = [],
}: FilterBarProps) {
  return (
    <div className="flex flex-col sm:flex-row gap-3 p-4 bg-white border-b">
      {/* Search Input */}
      {onSearchChange && (
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder={searchPlaceholder}
            value={searchValue}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-9"
          />
        </div>
      )}

      {/* Filter Dropdowns */}
      <div className="flex gap-2 flex-wrap">
        {filters.map((filter) => (
          <DropdownMenu key={filter.label}>
            <DropdownMenuTrigger className="min-w-[120px] h-9 px-3 text-sm border border-input bg-background hover:bg-accent hover:text-accent-foreground rounded-md">
              {filter.options.find((opt) => opt.value === filter.value)?.label || filter.label}
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              {filter.options.map((option) => (
                <DropdownMenuItem
                  key={option.value}
                  onClick={() => filter.onChange(option.value)}
                  className={filter.value === option.value ? 'bg-secondary' : ''}
                >
                  {option.label}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        ))}
      </div>
    </div>
  )
}
