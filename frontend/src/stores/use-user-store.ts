import { create } from 'zustand'

export type UserStats = {
  streak: number
  xp: number
  elo: number
}

type TodayMission = {
  title: string
  description: string
}

export type { UserStats, TodayMission }

export const useStreakXPELO = create<UserStats & { todayMission: TodayMission | null }>((set) => ({
  streak: 0,
  xp: 0,
  elo: 1200,
  todayMission: null,
}))