import * as React from 'react'
import { useUserStore } from '@/stores/use-user-store'
import { Button, Badge } from '@/components/uI'
import { useDownload } from '@/lib/hooks'

interface MissionHistoryItem {
  mission_id: string
  title: string
  date: string
  grade: 'S' | 'A' | 'B' | 'C' | 'F'
  xp_earned: number
  elo_change: number
  mode: string
  tier: number
}

export const MissionHistory: React.FC = () => {
  const { aiHistory, user } = useUserStore()
  const [filterTier, setFilterTier] = React.useState<number | null>(null)
  const [filterMode, setFilterMode] = React.useState<string | null>(null)
  const [searchQuery, setSearchQuery] = React.useState('')

  const filtered = React.useMemo(() => {
    return (aiHistory || [])
      .filter((item) => {
        if (filterTier !== null && item.tier !== filterTier) return false
        if (filterMode !== null && item.mode !== filterMode) return false
        if (searchQuery && !item.title.toLowerCase().includes(searchQuery.toLowerCase())) return false
        return true
      })
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
  }, [aiHistory, filterTier, filterMode, searchQuery])

  const columns = [
    { key: 'title', label: 'Mission Title', width: '40%' },
    { key: 'date', label: 'Date', width: '15%' },
    { key: 'grade', label: 'Grade', width: '10%' },
    { key: 'xp_earned', label: 'XP', width: '10%' },
    { key: 'elo_change', label: 'Elo Δ', width: '10%' },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4 px-4 py-2 border-b">
        <h2 className="text-lg font-medium">Mission History</h2>

        <div className="flex items-center gap-2">
          <select
            onChange={(e) => setFilterTier(Number(e.target.value))}
            className="border rounded px-3 py-2"
          >
            <option value="">All Tiers</option>
            {Array.from({ length: 5 }, (_, i) => i).map((tier) => (
              <option key={tier} value={tier}>
                Tier {tier}
              </option>
            ))}
          </select>

          <select
            onChange={(e) => setFilterMode(e.target.value)}
            className="border rounded px-3 py-2"
          >
            <option value="">All Modes</option>
            {['fix_bug', 'build_feature', 'refactor'].map((mode) => (
              <option key={mode} value={mode}>
                {mode}
              </option>
            ))}
          </select>

          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search missions..."
            className="border rounded px-3 py-2 flex-1"
          />
        </div>
      </div>

      {filtered.length === 0
        ? <p className="text-muted-foreground text-center py-8">No missions found</p>
        : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr>
                  {columns.map((col) => (
                    <th key={col.key} className="text-left p-3 border bottom">
                      {col.label}
                    </th>
                  ))}
                  <th className="text-right p-3 border bottom">Details</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((item) => (
                  <tr key={item.mission_id} className="border-y">
                    <td className="p-3">{item.title}</td>
                    <td className="p-3">{item.date}</td>
                    <td className="p-3">
                      <Badge
                        variant={
                          item.grade === 'S'
                            ? 'default'
                            : item.grade === 'A'
                              ? 'default'
                              : item.grade === 'B'
                                ? 'secondary'
                                : item.grade === 'C'
                                  ? 'secondary'
                                  : 'destructive'
                        }
                      >
                        {item.grade}
                      </Badge>
                    </td>
                    <td className="p-3">{item.xp_earned}</td>
                    <td className="p-3">{item.elo_change}</td>
                    <td className="p-3 text-right">
                      <Button
                        variant="link"
                        size="tiny"
                        className="text-xs"
                        onClick={() => console.log('Export', item)}
                      >
                        View
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

      <div className="flex justify-end px-4 py-2">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => console.log('CSV export')}
          className="hidden sm:block"
        >
          Export CSV
        </Button>
      </div>
    </div>
  )
}