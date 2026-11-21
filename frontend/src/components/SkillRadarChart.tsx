import * as React from 'react'

type SkillDimension = 'logic' | 'clean_code' | 'debugging' | 'testing' | 'performance'

interface SkillRadarChartProps {
  values: Record<SkillDimension, number>
  goals?: Record<SkillDimension, number>
}

const dimensionLabels = ['Logic', 'Clean Code', 'Debugging', 'Testing', 'Performance']
const dimensionKeys: SkillDimension[] = ['logic', 'clean_code', 'debugging', 'testing', 'performance']
const dimensionMax = 100

const angleStep = (2 * Math.PI) / dimensionLabels.length
const angles = dimensionLabels.map((_, i) => i * angleStep - Math.PI / 2)

export const SkillRadarChart: React.FC<SkillRadarChartProps> = ({ values, goals }) => {
  const radarWidth = 200
  const radarHeight = 200

  const points = React.useMemo(() => {
    const plotPoints: [number, number][] = []
    dimensionKeys.forEach((dim, i) => {
      const value = Math.max(0, Math.min(dimensionMax, values?.[dim] ?? 0))
      const radius = (value / dimensionMax) * (Math.min(radarWidth, radarHeight) / 2 - 20)
      const x = radarWidth / 2 + radius * Math.cos(angles[i])
      const y = radarHeight / 2 + radius * Math.sin(angles[i])
      plotPoints.push([x, y])
    })
    return plotPoints
  }, [values])

  const goalPoints = React.useMemo(() => {
    if (!goals) return null
    const plotPoints: [number, number][] = []
    dimensionKeys.forEach((dim, i) => {
      const value = Math.max(0, Math.min(dimensionMax, goals?.[dim] ?? 0))
      const radius = (value / dimensionMax) * (Math.min(radarWidth, radarHeight) / 2 - 20)
      const x = radarWidth / 2 + radius * Math.cos(angles[i])
      const y = radarHeight / 2 + radius * Math.sin(angles[i])
      plotPoints.push([x, y])
    })
    return plotPoints
  }, [goals])

  const maxRadius = Math.min(radarWidth, radarHeight) / 2 - 20

  return (
    <svg
      viewBox="-55 -25 310 250"
      className="w-full max-w-[300px] h-auto"
    >
      {/* Lingkaran batas luar & grid dalam */}
      <circle cx={radarWidth / 2} cy={radarHeight / 2} r={maxRadius} fill="none" stroke="rgba(0,0,0,0.1)" strokeWidth={1} />
      <circle cx={radarWidth / 2} cy={radarHeight / 2} r={maxRadius * 0.5} fill="none" stroke="rgba(0,0,0,0.06)" strokeWidth={1} />

      {/* Garis sumbu 5 dimensi */}
      {dimensionLabels.map((_, i) => (
        <line
          key={i}
          x1={radarWidth / 2}
          y1={radarHeight / 2}
          x2={radarWidth / 2 + maxRadius * Math.cos(angles[i])}
          y2={radarHeight / 2 + maxRadius * Math.sin(angles[i])}
          stroke="rgba(0,0,0,0.1)"
          strokeWidth={1}
        />
      ))}

      {/* Poligon skill saat ini */}
      {points.length > 0 && (
        <polygon
          points={points.map(([x, y]) => `${x},${y}`).join(' ')}
          fill="rgba(59, 130, 246, 0.25)"
          stroke="#3b82f6"
          strokeWidth={2}
        />
      )}

      {/* Poligon target (jika ada) */}
      {goalPoints && goalPoints.length > 0 && (
        <polygon
          points={goalPoints.map(([x, y]) => `${x},${y}`).join(' ')}
          fill="rgba(16, 185, 129, 0.2)"
          stroke="#10b981"
          strokeWidth={2}
          strokeDasharray="5, 5"
        />
      )}

      {/* Label 5 dimensi (tanpa stroke agar bersih & terbaca) */}
      {dimensionLabels.map((label, i) => (
        <text
          key={i}
          x={radarWidth / 2 + (maxRadius + 18) * Math.cos(angles[i])}
          y={radarHeight / 2 + (maxRadius + 14) * Math.sin(angles[i])}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize={11}
          fontWeight="600"
          fill="#334155"
          stroke="none"
        >
          {label}
        </text>
      ))}
    </svg>
  )
}
