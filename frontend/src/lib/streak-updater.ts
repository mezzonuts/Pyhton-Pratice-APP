import { useUserStore } from '@/stores/use-user-store'

export interface GradeResult {
  mission_id: string
  grade: string
  elo_change: number
  xp_earned: number
  skill_radar_delta: {
    logic: number
    clean_code: number
    debugging: number
    testing: number
    performance: number
  }
}

export interface FreezeShieldState {
  currentStreak: number
  longestStreak: number
  freezeShields: number
  freezeShieldClaimedThisWeek: boolean
  weekStartDate: Date
}

export class StreakUpdater {
  private store = useUserStore.getState()
  private storeSetter = useUserStore.setState

  async submitGradeResult(result: GradeResult): Promise<void> {
    try {
      const res = await fetch('http://localhost:8000/api/v1/missions/daily/grade-result', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mission_id: result.mission_id,
          grade: result.grade,
          elo_change: result.elo_change,
          xp_earned: result.xp_earned,
          skill_radar_delta: result.skill_radar_delta,
        }),
      })

      if (res.ok) {
        const data = await res.json()
        this.updateStores(data)
      } else {
        console.error('Failed to submit grade result', res.status)
      }
    } catch (e) {
      console.error('Error submitting grade result', e)
    }
  }

  private updateStores(data: any): void {
    const { currentStreak, longestStreak, freezeShields } = data

    this.storeSetter.set({
      currentStreak,
      longestStreak,
      freezeShields,
    })

    // Handle freeze shield logic (weekly claim Sat/Sun)
    this.handleFreezeShieldLogic()
  }

  private handleFreezeShieldLogic(): void {
    const now = new Date()
    const dayOfWeek = now.getDay() // 0=Sun, 1=Mon, ..., 5=Sat, 6=Sun
    const isWeekend = dayOfWeek === 5 || dayOfWeek === 6 // Sat or Sun

    // If it's weekend and freeze shield not claimed this week, grant it
    if (isWeekend && this.store.freezeShields < 3) {
      // Check if already claimed this week
      if (!this.store.freezeShieldClaimedThisWeek) {
        this.storeSetter.set({
          freezeShields: this.store.freezeShields + 1,
          freezeShieldClaimedThisWeek: true,
        })
      }
    }

    // Reset freeze shield claim status on Monday
    if (dayOfWeek === 0) { // Sunday
      // Allow claiming, but don't auto-grant beyond weekend
    }
  }
}