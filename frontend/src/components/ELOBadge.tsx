import * as React from 'react'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/uI'

interface ELOBadgeProps {
  elo: number
  tier: number
}

const TIER_THRESHOLDS = [800, 900, 1100, 1250, 1400, 1600]
const TIER_NAMES = ['Beginner', 'Novice', 'Intermediate', 'Advanced', 'Expert', 'Master', 'Grandmaster']

function getTier(elo: number): number {
  let tier = 0
  for (let i = TIER_THRESHOLDS.length - 1; i >= 0; i--) {
    if (elo >= TIER_THRESHOLDS[i]) {
      tier = i + 1
      break
    }
  }
  return tier
}

function getNextTierThreshold(elo: number, tier: number): number {
  const next = TIER_THRESHOLDS[tier]
  return next !== undefined ? next : TIER_THRESHOLDS[TIER_THRESHOLDS.length - 1]
}

function getTierColor(tier: number): string {
  const colors = [
    'bg-gray-100 text-gray-800',
    'bg-blue-100 text-blue-800',
    'bg-green-100 text-green-800',
    'bg-yellow-100 text-yellow-800',
    'bg-orange-100 text-orange-800',
    'bg-red-100 text-red-800',
    'bg-purple-100 text-purple-800',
  ]
  return colors[tier] || colors[0]
}

export const ELOBadge: React.FC<ELOBadgeProps> = ({ elo, tier }) => {
  const nextThreshold = getNextTierThreshold(elo, tier)
  const tierName = TIER_NAMES[tier] || 'Beginner'
  const tierColor = getTierColor(tier)
  const progress = ((elo % nextThreshold) / nextThreshold) * 100

  return (
    <Badge className={tierColor}>
      <div className="flex items-baseline gap-1">
        <span className="text-sm font-medium">{elo} <span className="text-xs text-muted-foreground">Elo</span></span>
        <span className="text-xs text-muted-foreground">/{nextThreshold}</span>
      </div>
      <div className="mt-1 h-2 bg-secondary/50 rounded-full overflow-hidden">
        <div
          className={cn(
            'h-full rounded-full transition-all duration-500',
            progress >= 100 ? 'bg-primary w-full' : `w-${Math.max(1, Math.min(100, progress))}`
          )}
        ></div>
      </div>
      <div className="mt-1 text-xs text-muted-foreground">
        {tierName} {tier + 1}/7
      </div>
    </Badge>
  )
}