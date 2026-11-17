// @ts-nocheck
export interface PyodideInstance {
  pyodide: any
  ready: Promise<any>
  loadPackage: (pkg: string) => Promise<void>
  runPython: (code: string) => Promise<string>
}

let pyodidePromise: Promise<PyodideInstance> | null = null

export function usePyodide(): PyodideInstance {
  if (!pyodidePromise) {
    pyodidePromise = (async (): Promise<PyodideInstance> => {
      const pyodide = await (await import('pyodide')).loadPyodide({
        indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.27.1/full/',
      })

      ;(await pyodide).loadPackage('python-stdlib')

      const ready = new Promise<void>((resolve) => {
        const check = () => {
          if (pyodide.runPython) {
            resolve()
          } else {
            setTimeout(check, 100)
          }
        }
        check()
      })

      await ready

      const loadPackage = async (pkg: string): Promise<void> => {
        await pyodide.loadPackage(pkg)
      }

      const runPython = async (code: string): Promise<string> => {
        return pyodide.runPython(code)
      }

      return { pyodide, ready, loadPackage, runPython }
    })()
  }

  return pyodidePromise
}

export async function initPyodide(): Promise<PyodideInstance> {
  return usePyodide()
}