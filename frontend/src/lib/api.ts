import { useUserStore } from '@/stores/use-user-store'

const isDev = process.env.NEXT_PUBLIC_ENV === 'development'
const BASE_URL = isDev
  ? 'http://localhost:8000'
  : 'https://api.pyforge.app/v1'

const COOKIE_NAME = 'access_token'

export const api = {
  async getAuthToken(): Promise<string> {
    const { accessToken } = useUserStore.getState()
    if (accessToken) return accessToken

    // Read from cookie
    const cookies = document.cookie.split(';').reduce((acc: any, curr) => {
      const [key, ...value] = curr.trim().split('=')
      acc[key] = value.join('=')
      return acc
    }, {})

    return cookies[COOKIE_NAME] || ''
  },

  async submitMission(code: string, missionId: string): Promise<any> {
    const token = await this.getAuthToken()

    const res = await fetch(`${BASE_URL}/api/v1/missions/daily/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ code, mission_id: missionId }),
    })

    if (!res.ok) throw new Error('Mission submission failed')
    return res.json()
  },

  async getMissionResult(missionId: string): Promise<any> {
    const token = await this.getAuthToken()

    const res = await fetch(`${BASE_URL}/api/v1/missions/daily/${missionId}/result`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!res.ok) throw new Error('Failed to get mission result')
    return res.json()
  },

  async postGradeResult(result: {
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
  }): Promise<any> {
    const token = await this.getAuthToken()

    const res = await fetch(`${BASE_URL}/api/v1/missions/daily/grade-result`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(result),
    })

    if (!res.ok) throw new Error('Failed to post grade result')
    return res.json()
  },
}