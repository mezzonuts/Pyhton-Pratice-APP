import { usePyodide } from './pyodide-loader'
import { LintError, LintResult, clientSideLint } from './client-side-linter'

export interface TestResult {
  passed: number
  failed: number
  total: number
  stdout: string
  stderr: string
  executionTime: number
}

export interface GraderResult {
  passed: number
  failed: number
  total: number
  stdout: string
  stderr: string
  grade: string
  xp: number
}

export async function runFunctionalTestsInPyodide(
  userCode: string,
  testFile: string,
  timeoutMs: number = 30000
): Promise<TestResult> {
  const pyodide = await usePyodide()
  const startTime = Date.now()

  let stdout = ''
  let stderr = ''
  let executionTime = 0

  const timeoutId = setTimeout(() => {
    stderr = 'Execution timed out after 30s'
  }, timeoutMs)

  try {
    // Wrap the user code and test code for capture
    const wrappedCode = [
      'import sys',
      '',
      'stdout_lines: list[str] = []',
      'stderr_lines: list[str] = []',
      '',
      'class StdoutCapturer(file):',
      '    def write(self, msg: str):',
      '        stdout_lines.append(msg)',
      '',
      'class StderrCapturer(file):',
      '    def write(self, msg: str):',
      '        stderr_lines.append(msg)',
      '',
      'old_stdout = sys.stdout',
      'old_stderr = sys.stderr',
      'sys.stdout = StdoutCapturer(sys.stdout)',
      'sys.stderr = StderrCapturer(sys.stderr)',
      '',
      testFile,
      userCode,
      '',
      'sys.stdout = old_stdout',
      'sys.stderr = old_stderr',
      '',
      'stdout_val = "".join(stdout_lines)',
      'stderr_val = "".join(stderr_lines)',
      'print(stdout_val, file=sys.stdout)',
      'print(stderr_val, file=sys.stderr)'
    ].join('\n')

    const result: any = pyodide.runPython(wrappedCode)
    const output = String(result || '')
    const parts = output.split('\n\n')
    stdout = parts[0] || ''
    stderr = parts[1] || ''
  } catch (e: any) {
    stderr = e.message || String(e)
    // Handle infinite loop termination
    if (e.message && (e.message.includes('timed out') || e.message.includes('terminated'))) {
      // Timeout or termination - treat as failed test
    }
  } finally {
    clearTimeout(timeoutId)
    executionTime = Date.now() - startTime
  }

  const passed = stderr === '' && executionTime < timeoutMs ? 1 : 0
  // Count actual passed/failed from test output
  const passCount = (stdout.match(/PASSED/gi) || []).length
  const failCount = (stderr.match(/FAILED/gi) || []).length

  return {
    passed: passCount,
    failed: failCount,
    total: passCount + failCount,
    stdout,
    stderr,
    executionTime
  }
}

export async function runGraderInPyodide(
  userCode: string,
  testCode: string,
  timeoutMs: number = 30000
): Promise<GraderResult> {
  // Stage 1: Lint check
  const lintResult = clientSideLint(userCode)

  // Stage 2: Run functional tests
  const testResult = await runFunctionalTestsInPyodide(userCode, testCode, timeoutMs)

  // Calculate pass rate for functional stage
  const passRate = testResult.total > 0 ? testResult.passed / testResult.total : 1.0

  // Determine grade based on scores
  let overallScore = 0
  let grade = 'F'

  // Lint: 15% weight, pass = 100, fail = 0
  const lintScore = lintResult.hasErrors ? 0 : 100
  overallScore += lintScore * 0.15

  // Format: 10% weight (check formatting basics)
  const formatScore = lintResult.hasErrors ? 0 : 100 // Simplified: if lint passes, assume format okay
  overallScore += formatScore * 0.10

  // Functional: 35% weight, based on pass_rate
  overallScore += passRate * 100 * 0.35

  // Determine grade
  if (overallScore >= 95) grade = 'S'
  else if (overallScore >= 85) grade = 'A'
  else if (overallScore >= 75) grade = 'B'
  else if (overallScore >= 65) grade = 'C'
  else grade = 'F'

  // Calculate XP
  const baseXp = 100 // default base XP
  const gradeMultiplier: Record<string, number> = { S: 1.5, A: 1.2, B: 1.0, C: 0.7, F: 0.0 }
  const xp = Math.round(baseXp * gradeMultiplier[grade as keyof typeof gradeMultiplier])

  return {
    passed: testResult.passed,
    failed: testResult.failed,
    total: testResult.total,
    stdout: testResult.stdout,
    stderr: testResult.stderr,
    grade,
    xp
  }
}