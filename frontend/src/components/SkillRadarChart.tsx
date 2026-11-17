import * as React from 'react'

type SkillDimension = 'logic' | 'clean_code' | 'debugging' | 'testing' | 'performance'

interface SkillRadarChartProps {
  values: Record<SkillDimension, number>
  goals?: Record<SkillDimension, number>
}

const dimensionLabels = ['Logic', 'Clean Code', 'Debugging', 'Testing', 'Performance']
const dimensionMax = 100

const angleStep = (2 * Math.PI) / dimensionLabels.length
const angles = dimensionLabels.map((_, i) => i * angleStep - Math.PI / 2)

const dimensionColors = {
  logic: '#3b82f6',
  clean_code: '#10b981',
  debugging: '#f59e0b',
  testing: '#8b5cf6',
  performance: '#ec4899',
}

export const SkillRadarChart: React.FC<SkillRadarChartProps> = ({ values, goals }) => {
  const [radarWidth, setRadarWidth] = React.useState(200)
  const [radarHeight, setRadarHeight] = React.useState(200)

  const points = React.useMemo(() => {
    const plotPoints: number[] = []
    dimensionLabels.forEach((dim, i) => {
      const value = Math.max(0, Math.min(dimensionMax, values[dim as SkillDimension] ?? 0))
      const radius = (value / dimensionMax) * Math.min(radarWidth / 2, radarHeight / 2)
      const x = radarWidth / 2 + radius * Math.cos(angles[i])
      const y = radarHeight / 2 + radius * Math.sin(angles[i])
      plotPoints.push(x, y)
    })
    return plotPoints
  }, [values, radarWidth, radarHeight])

  const goalPoints = goals
    ? React.useMemo(() => {
        const plotPoints: number[] = []
        dimensionLabels.forEach((dim, i) => {
          const value = Math.max(0, Math.min(dimensionMax, goals[dim as SkillDimension] ?? 0))
          const radius = (value / dimensionMax) * Math.min(radarWidth / 2, radarHeight / 2)
          const x = radarWidth / 2 + radius * Math.cos(angles[i])
          const y = radarHeight / 2 + radius * Math.sin(angles[i])
          plotPoints.push(x, y)
        })
        return plotPoints
      }, [goals, radarWidth, radarHeight])
    : null

  return (
    <svg
      width={radarWidth}
      height={radarHeight}
      className="rounded-lg border"
    >
      <g fill="none" stroke="currentColor" strokeWidth={2}>
        {/* Radar polygon (current skills) */}
        {points.length > 0 && (
          <polygon
            points={points.map((p, i) => `${p},${points[i + 1] ?? points[0]}`).join(' ')}
            fill="rgba(59, 130, 246, 0.2)"
            stroke="#3b82f6"
          />
        )}

        {/* Goal polygon (if provided) */}
        {goalPoints && goalPoints.length > 0 && (
          <polygon
            points={goalPoints
              .map((p, i) => `${p},${goalPoints[i + 1] ?? goalPoints[0]}`)
              .join(' ')}
            fill="rgba(16, 185, 129, 0.2)"
            stroke="#10b981"
            strokeDasharray="5, 5"
          />
        )}

        {/* Axes lines */}
        {dimensionLabels.map((_, i) => (
          <line
            key={i}
            x1={radarWidth / 2}
            y1={radarHeight / 2}
            x2={radarWidth / 2 + (radarWidth / 2 - 20) * Math.cos(angles[i])}
            y2={radarHeight / 2 + (radarWidth / 2 - 20) * Math.sin(angles[i])}
            stroke="rgba(0, 0, 0, 0.1)"
            strokeWidth={1}
          />
        ))}

        {/* Dimension labels */}
        {dimensionLabels.map((label, i) => (
          <text
            key={i}
            x={radarWidth / 2 + (radarWidth / 2 - 10) * Math.cos(angles[i])}
            y={radarHeight / 2 + (radarWidth / 2 - 10) * Math.sin(angles[i])}
            textAnchor="middle"
            fontSize={12}
            fontWeight="bold"
          >
            {label}
          </text>
        ))}

        {/* Max value circle arcs */}
        <circle
          cx={radarWidth / 2}
          cy={radarHeight / 2}
          r={Math.min(radarWidth, radarHeight) / 2 - 2}
          fill="none"
          stroke="rgba(0, 0, 0, 0.1)"
          strokeWidth={1}
        />
      </g>
    </svg>
  )
}