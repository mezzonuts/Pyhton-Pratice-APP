import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { useStreakXPELO } from '@/stores/use-user-store'

export default function Dashboard() {
  const { streak, xp, elo, todayMission } = useStreakXPELO()

  return (
    <main className="max-w-7xl mx-auto p-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="col-span-1 lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Today's Mission</CardTitle>
            </CardHeader>
            <CardContent>
              {todayMission ? (
                <div>
                  <p>{todayMission.title}</p>
                  <p>{todayMission.description}</p>
                </div>
              ) : (
                <p>No mission assigned</p>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="col-span-1 lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Streak</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{streak} days</div>
            </CardContent>
          </Card>
        </div>

        <div className="col-span-1 lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>XP Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <Progress value={xp} max={100} />
              <div className="text-sm text-muted-foreground">{xp}%</div>
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="mt-6">
        <Card>
          <CardHeader>
            <CardTitle>ELO Rating</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge variant="secondary">{elo} <span className="text-sm text-muted-foreground">Elo</span></Badge>
          </CardContent>
        </Card>
      </div>
    </main>
  )
}