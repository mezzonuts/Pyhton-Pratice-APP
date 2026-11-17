import { useState, useEffect } from 'react'
import { useUserStore } from '@/stores/use-user-store'

export type MissionResult = {
  pass: boolean
  grade: number
  xp: number
  streak: number
}

export type MissionState = {
  mission: any
  loading: boolean
  submitted: boolean
  result: MissionResult | null
}

export const useMissionHook = () => {
  const { user, streak, xp, elo, submitMissionResult } = useUserStore()
  const [mission, setMission] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [submitted, setSubmitted] = useState(false)
  const [result, setResult] = useState<MissionResult | null>(null)

  useEffect(() => {
    fetchMission()
  }, [user])

  const fetchMission = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/v1/missions/daily')
      if (res.ok) {
        const data = await res.json()
        setMission(data)
      }
    } catch (e) {
      console.error('Failed to fetch mission', e)
    } finally {
      setLoading(false)
    }
  }

  const submitCode = async (code: string) => {
    setSubmitted(true)
    try {
      const res = await fetch('/api/v1/missions/daily/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${user?.accessToken}`
        },
        body: JSON.stringify({ code })
      })
      if (res.ok) {
        const data = await res.json()
        setResult({
          pass: data.pass,
          grade: data.grade,
          xp: data.xp,
          streak: data.streak ?? streak
        })
        submitMissionResult({
          pass: data.pass,
          grade: data.grade,
          xp: data.xp,
          streak: data.streak ?? 0
        })
      }
    } catch (e) {
      console.error('Mission submission failed', e)
    } finally {
      setSubmitted(false)
    }
  }

  return {
    mission,
    loading,
    submitted,
    result,
    fetchMission,
    submitCode
  }
}