'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/uI/card'
import { Progress } from '@/components/uI/progress'
import { Badge } from '@/components/uI/badge'
import { DailyMissionCard } from '@/components/DailyMissionCard'
import { SkillRadarChart } from '@/components/SkillRadarChart'
import { MissionHistory } from '@/components/MissionHistory'
import { ELOBadge } from '@/components/ELOBadge'
import { useUserStore } from '@/stores/use-user-store'

export default function Dashboard() {
  const {
    streak,
    longestStreak,
    freezeShields,
    xp,
    progress,
    elo,
    overallScore,
    strongestDimension,
    weakestDimension,
    skillRadar,
  } = useUserStore()

  const { mission, loading, submitted, result } = useUserStore()

  return (
    <main className="max-w-7xl mx-auto p-6 bg-background min-h-screen">
      <div className="grid min-h-screen grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="lg:col-span-2">
          <HeaderBar streak={streak} longestStreak={longestStreak} freezeShields={freezeShields} xp={xp} elo={elo} skillRadar={skillRadar} />
        </div>

        <div className="lg:col-span-2">
          <div className="grid grid-cols-1 gap-6">
            <div>
              <DailyMissionCard />
              <SkillRadarChart values={skillRadar} />
            </div>

            <div>
              <MissionHistory />
              <div className="mt-4"><div className="text-sm font-medium mb-1">XP Progress ({xp} XP)</div><Progress value={xp % 100} /></div>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

function HeaderBar({
  streak,
  longestStreak,
  freezeShields,
  xp,
  elo,
  skillRadar,
}: {
  streak: number
  longestStreak: number
  freezeShields: number
  xp: number
  elo: number
  skillRadar?: any
}) {
  const tier = skillRadar ? Math.min(6, Math.max(0, TIER_INDEX[elo] ?? 0)) : 0

  return (
    <div className="bg-card rounded-lg p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
            <Badge variant="default" className="text-sm">
              {skillRadar?.logic > 0 ? 'U' : '?' }
            </Badge>
          </div>
          <div>
            <h2 className="text-xl font-bold">PyForge Daily</h2>
            <p className="text-sm text-muted-foreground">Code daily, level up weekly</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <ELOBadge elo={elo} tier={tier} />
          <div className="flex items-center gap-2">
            <span className="text-xl font-bold">{streak}</span>
            <Badge variant="secondary">{longestStreak}+</Badge>
            {freezeShields > 0 && (
              <Badge variant="default">
                <svg
                  className="h-4 w-4"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path d="M9 12l2 2 4-4m5.618-4.016a7.967 7.967 0 0 1-1.167 1.167l-2.082 2.082 1.538 1.538a7.966 7.966 0 0 1-1.108 1.107l-2.082 2.082-1.538 1.538m14.7 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                </svg>
                Freeze
              </Badge>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div>
          <div className="text-sm text-muted-foreground">Streak</div>
          <div className="text-2xl font-bold">{streak} days</div>
        </div>
        <div>
          <div className="text-sm text-muted-foreground">Longest</div>
          <div className="text-2xl font-bold">{longestStreak}+ days</div>
        </div>
        <div>
          <div className="text-sm text-muted-foreground">Progress</div>
          <div className="h-2 bg-secondary/50 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary rounded-full"
              style={{ width: `${(xp % 100) / 100 * 100}%` }}
            ></div>
          </div>
          <div className="text-xs text-muted-foreground">{xp % 100}%</div>
        </div>
      </div>
    </div>
  )
}

const TIER_INDEX: Record<number, number> = {
  1000: 0,
  1100: 1,
  1250: 2,
  1400: 3,
  1600: 4,
}