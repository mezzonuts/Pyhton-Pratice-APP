import { MonacoEditor } from '@/components/MonacoEditor'
import { useMissionHook } from '@/lib/use-mission-hook'
import { useState, useEffect } from 'react'
import { Badge } from '@/components/uI/badge'
import { Progress } from '@/components/uI/progress'
import { Card, CardHeader, CardContent, CardTitle } from '@/components/uI/card'
import { clientSideLint, LintError, LintResult } from '@/lib/client-side-linter'
import { runGraderInPyodide } from '@/lib/client-side-grader'

export const DailyMissionCard: React.FC = () => {
  const { mission, loading, submitted, result, fetchMission } = useMissionHook()
  const [code, setCode] = useState('')
  const [lintErrors, setLintErrors] = useState<LintError[]>([])
  const [testResult, setTestResult] = useState<{
    passed: number
    failed: number
    total: number
    grade: string
    xp: number
  } | null>(null)
  const [runTests, setRunTests] = useState(false)

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Today's Mission</CardTitle>
        </CardHeader>
        <CardContent>Loading mission...</CardContent>
      </Card>
    )
  }

  if (!mission) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Today's Mission</CardTitle>
        </CardHeader>
        <CardContent>No mission assigned</CardContent>
      </Card>
    )
  }

  // Run lint on code change
  useEffect(() => {
    const result = clientSideLint(code)
    setLintErrors(result.errors)
  }, [code])

  return (
    <Card>
      <CardHeader>
        <CardTitle>{mission.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{mission.description}</p>

        <MonacoEditor
          defaultValue={code}
          onChange={(value) => {
            setCode(value)
            setLintErrors([])
            setTestResult(null)
          }}
          language="python"
          readOnly={submitted}
        />

        <div className="mt-4">
          {lintErrors.length > 0 && (
            <div className="mb-2 text-xs text-muted-foreground">
              {lintErrors.length} lint error(s) found
            </div>
          )}

          {lintErrors.length > 0 && lintErrors.map((err) => (
            <div key={err.code} className="mt-1 text-xs">
              Line {err.line}:{err.column} - {err.code}: {err.message}
            </div>
          ))}

          <button
            onClick={() => setRunTests(true)}
            disabled={submitted || !mission}
            className="btn-primary"
          >
            {runTests ? 'Running Tests...' : 'Run Tests'}
          </button>
        </div>

        {runTests && !submitted && (
          <div className="mt-4 p-3 bg-secondary/20 rounded">
            <h4 className="text-sm font-medium mb-2">Test Progress</h4>
            {testResult && (
              <div>
                <p>Passed: {testResult.passed}/{testResult.total}</p>
                <p>Grade: {testResult.grade}</p>
                <p>XP: +{testResult.xp}</p>
              </div>
            )}
            {!testResult && <p className="text-xs text-muted-foreground">Running tests...</p>}
          </div>
        )}
      </CardContent>

      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Result</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Grade: {result.grade}%</p>
            <Badge variant={result.pass ? 'default' : 'secondary'}>
              {result.pass ? 'Pass' : 'Fail'}
            </Badge>
            <p>XP: +{result.xp}</p>
            <p>Streak: {result.streak} days</p>
          </CardContent>
        </Card>
      )}
    </Card>
  )
}