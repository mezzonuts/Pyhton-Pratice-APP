export interface ScoreCalculatorInput {
  lintScore: number
  formatScore: number
  typecheckScore: number
  functionalScore: number
  performanceScore: number
  qualityScore: number
  baseXp: number
}

export interface ScoreCalculatorOutput {
  grade: string
  xp: number
  eloChange: number
  stageResults: StageResult[]
  totalScore: number
}

export interface StageWeights {
  lint: number
  format: number
  typecheck: number
  functional: number
  performance: number
  quality: number
}

export const STAGE_WEIGHTS: StageWeights = {
  lint: 0.15,
  format: 0.10,
  typecheck: 0.20,
  functional: 0.35,
  performance: 0.10,
  quality: 0.10,
}

export const GRADE_THRESHOLDS = {
  S: 90,
  A: 80,
  B: 70,
  C: 60,
  F: 60,
}

export const GRADE_MULTIPLIERS = {
  S: 1.5,
  A: 1.2,
  B: 1.0,
  C: 0.7,
  F: 0.0,
}

export interface StageResult {
  stage: string
  status: 'passed' | 'failed'
  score: number
  weight: number
  details: string
}

export function calculateGrade(input: ScoreCalculatorInput): ScoreCalculatorOutput {
  const {
    lintScore,
    formatScore,
    typecheckScore,
    functionalScore,
    performanceScore,
    qualityScore,
    baseXp,
  } = input

  // Stage 1: Lint (15% weight)
  const lintWeighted = lintScore * STAGE_WEIGHTS.lint

  // Stage 2: Format (10% weight)
  const formatWeighted = formatScore * STAGE_WEIGHTS.format

  // Stage 3: Typecheck (20% weight)
  const typecheckWeighted = typecheckScore * STAGE_WEIGHTS.typecheck

  // Stage 4: Functional (35% weight)
  const functionalWeighted = functionalScore * STAGE_WEIGHTS.functional

  // Stage 5: Performance (10% weight)
  const performanceWeighted = performanceScore * STAGE_WEIGHTS.performance

  // Stage 6: Quality (10% weight)
  const qualityWeighted = qualityScore * STAGE_WEIGHTS.quality

  // Calculate total weighted score
  const totalScore = lintWeighted + formatWeighted + typecheckWeighted + functionalWeighted + performanceWeighted + qualityWeighted

  // Determine grade
  let grade: string
  if (totalScore >= GRADE_THRESHOLDS.S) grade = 'S'
  else if (totalScore >= GRADE_THRESHOLDS.A) grade = 'A'
  else if (totalScore >= GRADE_THRESHOLDS.B) grade = 'B'
  else if (totalScore >= GRADE_THRESHOLDS.C) grade = 'C'
  else grade = 'F'

  // Calculate XP reward
  const multiplier = GRADE_MULTIPLIERS[grade as keyof typeof GRADE_MULTIPLIERS]
  const xp = Math.round(baseXp * multiplier)

  // Calculate Elo change
  const eloChangeMap: Record<string, number> = { S: 25, A: 15, B: 8, C: 3, F: -10 }
  const eloChange = eloChangeMap[grade as keyof typeof eloChangeMap]

  // Build stage results
  const stageResults: StageResult[] = [
    {
      stage: 'lint',
      status: lintScore >= 80 ? 'passed' : 'failed',
      score: lintScore,
      weight: STAGE_WEIGHTS.lint,
      details: lintScore >= 80 ? '0 lint errors' : 'lint errors detected',
    },
    {
      stage: 'format',
      status: formatScore >= 80 ? 'passed' : 'failed',
      score: formatScore,
      weight: STAGE_WEIGHTS.format,
      details: formatScore >= 80 ? '0 format diffs' : 'format issues detected',
    },
    {
      stage: 'typecheck',
      status: typecheckScore >= 80 ? 'passed' : 'failed',
      score: typecheckScore,
      weight: STAGE_WEIGHTS.typecheck,
      details: typecheckScore >= 80 ? '0 type errors' : 'type errors detected',
    },
    {
      stage: 'functional',
      status: functionalScore >= 80 ? 'passed' : 'failed',
      score: functionalScore,
      weight: STAGE_WEIGHTS.functional,
      details: `${functionalScore}% functional`,
    },
    {
      stage: 'performance',
      status: performanceScore >= 80 ? 'passed' : 'failed',
      score: performanceScore,
      weight: STAGE_WEIGHTS.performance,
      details: `${performanceScore}% performance`,
    },
    {
      stage: 'quality',
      status: qualityScore >= 80 ? 'passed' : 'failed',
      score: qualityScore,
      weight: STAGE_WEIGHTS.quality,
      details: `${qualityScore}% quality`,
    },
  ]

  return {
    grade,
    xp,
    eloChange,
    stageResults,
    totalScore,
  }
}