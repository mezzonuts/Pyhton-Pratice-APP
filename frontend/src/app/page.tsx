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
    elo,
    skillRadar,
  } = useUserStore()

  return (
    <main className="max-w-7xl mx-auto px-6 pb-12 space-y-6">
      <HeaderBar
        streak={streak}
        longestStreak={longestStreak}
        freezeShields={freezeShields}
        xp={xp}
        elo={elo}
        skillRadar={skillRadar}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        <div className="lg:col-span-2">
          <DailyMissionCard />
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Skill Radar</CardTitle>
          </CardHeader>
          <CardContent className="flex justify-center">
            <SkillRadarChart values={skillRadar} />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6 space-y-4">
          <MissionHistory />
          <div className="pt-2 border-t">
            <div className="flex justify-between text-sm font-medium mb-2">
              <span>XP Progress</span>
              <span>{xp} XP</span>
            </div>
            <Progress value={xp % 100} />
          </div>
        </CardContent>
      </Card>
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
    <div className="bg-card rounded-lg border p-6 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold">
            {skillRadar?.logic > 0 ? 'U' : 'P'}
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
              <Badge variant="default">Freeze</Badge>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <div className="text-sm text-muted-foreground">Streak</div>
          <div className="text-2xl font-bold">{streak} days</div>
        </div>
        <div>
          <div className="text-sm text-muted-foreground">Longest</div>
          <div className="text-2xl font-bold">{longestStreak}+ days</div>
        </div>
        <div>
          <div className="text-sm text-muted-foreground mb-1">Progress</div>
          <div className="h-2 bg-secondary rounded-full overflow-hidden">
            <div
              className="h-full bg-primary rounded-full"
              style={{ width: `${xp % 100}%` }}
            ></div>
          </div>
          <div className="text-xs text-muted-foreground mt-1">{xp % 100}%</div>
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
