import { usePyodide } from './pyodide-loader'

export interface TestResult {
  pass: boolean
  stdout: string
  stderr: string
  executionTime: number
}

export async function runTestsInPyodide(
  pythonCode: string,
  testCode: string,
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
      testCode,
      pythonCode,
      '',
      'sys.stdout = old_stdout',
      'sys.stderr = old_stderr',
      '',
      'stdout_val = "".join(stdout_lines)',
      'stderr_val = "".join(stderr_lines)',
      'print(stdout_val)',
      'print(stderr_val, file=sys.stderr)'
    ].join('\n')

    const result: any = pyodide.runPython(wrappedCode)
    const output = String(result || '')
    const parts = output.split('\n\n')
    stdout = parts[0] || ''
    stderr = parts[1] || ''
  } catch (e: any) {
    stderr = e.message || String(e)
  } finally {
    clearTimeout(timeoutId)
    executionTime = Date.now() - startTime
  }

  const pass = stderr === '' && executionTime < timeoutMs

  return { pass, stdout, stderr, executionTime }
}