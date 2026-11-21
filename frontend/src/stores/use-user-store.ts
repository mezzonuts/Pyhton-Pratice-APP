// @ts-nocheck
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

export type { TodayMission }

interface MissionResult {
  pass: boolean
  grade: number
  xp: number
  streak: number
}

interface AIProvider {
  id: string
  type: string
  name: string
  base_url: string
  model: string
  is_default: boolean
  priority: number
}

interface AiHistoryItem {
  id: string
  type: 'hint' | 'review' | 'problem'
  content: string
  created_at: string
}

interface SkillRadar {
  logic: number
  clean_code: number
  debugging: number
  testing: number
  performance: number
}

interface UserState {
  user: any | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  login: (user: any, accessToken: string, refreshToken: string) => void
  logout: () => void
  initFromStore: () => void
  refreshTokenSilent: () => Promise<boolean>
  submitMissionResult: (result: MissionResult) => Promise<void>
  onMissionGrade: (gradeResult: {
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
  }) => void
  get streak(): number
  get xp(): number
  get elo(): number
  get overallScore(): number
  get strongestDimension(): keyof SkillRadar
  get weakestDimension(): keyof SkillRadar
  aiProviders: AIProvider[]
  setProviders: (providers: AIProvider[]) => void
  selectProvider: (providerId: string) => void
  clearAIHistory: () => void
}

const COOKIE_NAME_ACCESS = 'access_token'
const COOKIE_NAME_REFRESH = 'refresh_token'

function updateStats(current: number, delta: number): number {
  return Math.max(0, current + delta)
}

function computeOverallScore(radar: SkillRadar): number {
  return (
    radar.logic * 0.2 +
    radar.clean_code * 0.2 +
    radar.debugging * 0.2 +
    radar.testing * 0.2 +
    radar.performance * 0.2
  )
}

function findStrongestDimension(radar: SkillRadar): keyof SkillRadar {
  const values = { logic: radar.logic, clean_code: radar.clean_code, debugging: radar.debugging, testing: radar.testing, performance: radar.performance }
  return Object.keys(values).reduce((a, b) => (values[a] > values[b] ? a : b))
}

function findWeakestDimension(radar: SkillRadar): keyof SkillRadar {
  const values = { logic: radar.logic, clean_code: radar.clean_code, debugging: radar.debugging, testing: radar.testing, performance: radar.performance }
  return Object.keys(values).reduce((a, b) => (values[a] < values[b] ? a : b))
}

export const useUserStore = create<UserState>((set, get) => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  skills: {
    logic: 0,
    clean_code: 0,
    debugging: 0,
    testing: 0,
    performance: 0,
  },
  skillRadar: {
    logic: 0,
    clean_code: 0,
    debugging: 0,
    testing: 0,
    performance: 0,
  },
  streak: 0,
  longestStreak: 0,
  freezeShields: 0,
  xp: 0,
  progress: 0,
  elo: 1000,
  overallScore: 0,
  strongestDimension: 'logic',
  weakestDimension: 'logic',

  localStorageKey: 'pyforge-user-state',

  login: (user, accessToken, refreshToken) => {
    document.cookie = `${COOKIE_NAME_ACCESS}=${accessToken};path=/;max-age=${15 * 60}`
    document.cookie = `${COOKIE_NAME_REFRESH}=${refreshToken};path=/;max-age=${7 * 24 * 60 * 60}`
    const now = new Date().getTime()
    localStorage.setItem(this.localStorageKey, JSON.stringify({
      user, accessToken, refreshToken, isAuthenticated: true,
      streak, longestStreak, freezeShields, xp, progress, elo,
      skillRadar: get().skillRadar,
    }))
    set({ user, accessToken, refreshToken, isAuthenticated: true, streak, longestStreak, freezeShields, xp, progress, elo, skillRadar: get().skillRadar })
  },
  logout: () => {
    document.cookie = `${COOKIE_NAME_ACCESS}=;path=/;max-age=0;expires=Thu, 01 Jan 1970 00:00:00 GMT`
    document.cookie = `${COOKIE_NAME_REFRESH}=;path=/;max-age=0;expires=Thu, 01 Jan 1970 00:00:00 GMT`
    localStorage.removeItem(this.localStorageKey)
    set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false, streak: 0, longestStreak: 0, freezeShields: 0, xp: 0, progress: 0, elo: 1000, skillRadar: { logic: 0, clean_code: 0, debugging: 0, testing: 0, performance: 0 } })
  },
  initFromStore: () => {
    const stored = localStorage.getItem(this.localStorageKey)
    if (stored) {
      const data = JSON.parse(stored)
      set({
        user: data.user,
        accessToken: data.accessToken,
        refreshToken: data.refreshToken,
        isAuthenticated: data.isAuthenticated ?? false,
        streak: data.streak ?? 0,
        longestStreak: data.longestStreak ?? 0,
        freezeShields: data.freezeShields ?? 0,
        xp: data.xp ?? 0,
        progress: data.progress ?? 0,
        elo: data.elo ?? 1000,
        skillRadar: data.skillRadar ?? {
          logic: 0, clean_code: 0, debugging: 0, testing: 0, performance: 0,
        },
      })
    }
  },
  refreshTokenSilent: async () => {
    const { refreshToken } = get()
    if (!refreshToken) return false
    try {
      const res = await fetch('http://localhost:8000/auth/me', {
        headers: { Authorization: `Bearer ${refreshToken}` },
      })
      if (res.ok) {
        const user = await res.json()
        const newAccessToken = user.access_token || refreshToken
        document.cookie = `${COOKIE_NAME_ACCESS}=${newAccessToken};path=/;max-age=${15 * 60}`
        set({ accessToken: newAccessToken })
        return true
      }
      return false
    } catch {
      return false
    }
  },
  submitMissionResult: async (result: MissionResult) => {
    try {
      const res = await fetch('/api/v1/missions/daily/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(result),
      })
      if (res.ok) {
        const data = await res.json()
        set({
          streak: updateStats(get().streak, data.streak_delta ?? 0),
          longestStreak: Math.max(get().longestStreak, get().streak + 1),
          xp: updateStats(get().xp, data.xp_gain ?? result.xp),
          progress: get().xp % 100,
          elo: data.elo_rating ?? get().elo,
          freezeShields: data.freeze_shields ?? get().freezeShields,
          skillRadar: {
            logic: data.skill_radar?.logic ?? get().skillRadar.logic,
            clean_code: data.skill_radar?.clean_code ?? get().skillRadar.clean_code,
            debugging: data.skill_radar?.debugging ?? get().skillRadar.debugging,
            testing: data.skill_radar?.testing ?? get().skillRadar.testing,
            performance: data.skill_radar?.performance ?? get().skillRadar.performance,
          },
        })
      }
    } catch (e) {
      console.error('Failed to submit mission result', e)
    }
  },
  onMissionGrade: (gradeResult) => {
    const { grade, elo_change, xp_earned, skill_radar_delta } = gradeResult
    const { streak, xp, elo, skillRadar } = get()

    // Update local store
    set({
      streak: updateStats(streak, 1), // +1 for completed mission
      longestStreak: Math.max(get().longestStreak, streak + 1),
      xp: updateStats(xp, xp_earned),
      progress: get().progress + xp_earned,
      elo: elo + elo_change,
      freezeShields: get().freezeShields,
    })

    // Update skill radar via delta
    const skillDelta = skill_radar_delta
    const updatedSkills = {
      logic: (skillRadar?.logic ?? 0) + skillDelta.logic,
      clean_code: (skillRadar?.clean_code ?? 0) + skillDelta.clean_code,
      debugging: (skillRadar?.debugging ?? 0) + skillDelta.debugging,
      testing: (skillRadar?.testing ?? 0) + skillDelta.testing,
      performance: (skillRadar?.performance ?? 0) + skillDelta.performance,
    }

    // Cap skills at 0-100
    const cappedSkills = {
      logic: Math.max(0, Math.min(100, updatedSkills.logic)),
      clean_code: Math.max(0, Math.min(100, updatedSkills.clean_code)),
      debugging: Math.max(0, Math.min(100, updatedSkills.debugging)),
      testing: Math.max(0, Math.min(100, updatedSkills.testing)),
      performance: Math.max(0, Math.min(100, updatedSkills.performance)),
    }

    // Update the store with new skill values and recomputed getters
    const newStrongest = findStrongestDimension(cappedSkills)
    const newWeakest = findWeakestDimension(cappedSkills)
    const overallScore = computeOverallScore(cappedSkills)

    set({
      skills: cappedSkills,
      skillRadar: cappedSkills,
      overallScore,
      strongestDimension: newStrongest,
      weakestDimension: newWeakest,
    })
  },
  selectProvider: (providerId: string) => {
    const { aiProviders } = get()
    const provider = aiProviders.find((p) => p.id === providerId)
    if (provider) {
      set({ selectedProvider: provider })
    }
  },
  clearAIHistory: () => {
    set({ aiHistory: [] })
  },
  aiProviders: [],
  setProviders: (providers: AIProvider[]) => {
    set({ aiProviders: providers })
  },
  aiHistory: [],
  addAIHistory: (item: AiHistoryItem) => {
    set((state) => ({
      aiHistory: [...state.aiHistory, item],
    }))
  },
  get streak() {
    const { user } = get()
    return user?.streak_days ?? 0
  },
  get xp() {
    const { user } = get()
    return user?.total_xp ?? 0
  },
  get elo() {
    const { user } = get()
    return user?.elo_rating ?? 1000
  },
  get overallScore() {
    const { skillRadar } = get()
    return computeOverallScore(skillRadar)
  },
  get strongestDimension() {
    const { skillRadar } = get()
    return findStrongestDimension(skillRadar)
  },
  get weakestDimension() {
    const { skillRadar } = get()
    return findWeakestDimension(skillRadar)
  },
  skills: {
    logic: 0,
    clean_code: 0,
    debugging: 0,
    testing: 0,
    performance: 0,
  }
}))
