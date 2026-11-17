export interface LintError {
  line: number
  column: number
  code: string
  message: string
}

export interface LintResult {
  errors: LintError[]
  hasErrors: boolean
}

export function runRuffCheck(code: string): LintResult {
  const errors: LintError[] = []

  if (!code || code.trim() === '') {
    return { errors, hasErrors: false }
  }

  const lines = code.split('\n')

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const lineNumber = i + 1

    // Check for unused variables (simple pattern: variable assigned but never read)
    const unusedVarMatch = line.match(/^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?!.*)/m)
    if (unusedVarMatch) {
      const column = unusedVarMatch[1].length + 1
      errors.push({
        line: lineNumber,
        column,
        code: 'F841',
        message: `unused variable '${unusedVarMatch[2]}'`
      })
    }

    // Check for wrong indentation (mixed tabs and spaces, or indentation not multiple of 4)
    const stripped = line.replace(/^\s+/, '')
    if (stripped && line !== stripped) {
      const indent = line.substring(0, line.length - stripped.length)
      // Check for tabs in indentation
      if (indent.includes('\t')) {
        errors.push({
          line: lineNumber,
          column: 1,
          code: 'E101',
          message: 'Indentation contains mixed tabs and spaces'
        })
      }
      // Check if indent is multiple of 4 spaces
      const spaces = indent.length
      if (spaces % 4 !== 0 && /^[^\S\n]*$/.test(line) && stripped) {
        errors.push({
          line: lineNumber,
          column: 1,
          code: 'E101',
          message: 'Unindented block'
        })
      }
    }

    /* Check for missing docstring on function/class definitions */
    const defMatch = line.match(/^(?:\s*)(?:\ndef\s+|\bclass\s+)/)
    if (defMatch && lines[i + 1]) {
      const nextLine = lines[i + 1].trim()
      if (!nextLine.startsWith('"""') && !nextLine.startsWith("'''") && nextLine !== '') {
        errors.push({
          line: lineNumber,
          column: defMatch[0].length,
          code: 'D212',
          message: 'Missing docstring'
        })
      }
    }
  }

  return { errors, hasErrors: errors.length > 0 }
}

export function clientSideLint(code: string): LintResult {
  // Try to use ruff if available (in Pyodide environment)
  // If ruff is not available, fall back to regex-based linting
  
  // For now, use the regex-based fallback since ruff cannot run in WASM directly
  // without a full Python environment
  return runRuffCheck(code)
}

export function initializeRuffInPyodide(): Promise<boolean> {
  // Attempt to initialize ruff in Pyodide
  // ruff is a Python tool; in WASM/Pyodide we fall back to regex-based linting
  return Promise.resolve(false)
}