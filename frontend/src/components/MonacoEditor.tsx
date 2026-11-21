'use client'
// @ts-nocheck
import { useEffect, useRef } from 'react'

export const MonacoEditor: React.FC<{
  defaultValue?: string
  onChange?: (value: string) => void
  height?: string
  width?: string
  readOnly?: boolean
  language?: string
}> = ({
  defaultValue = '',
  onChange,
  height = '300px',
  width = '100%',
  readOnly = false,
  language = 'python',
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const editorRef = useRef<any>(null)

  useEffect(() => {
    let disposed = false
    let subscription: any = null

    import('monaco-editor').then((monaco) => {
      if (disposed || !containerRef.current) return
      const editor = monaco.editor.create(containerRef.current, {
        value: defaultValue,
        language,
        theme: 'vs-dark',
        automaticLayout: true,
        minimap: { enabled: true },
        readOnly,
      })
      editorRef.current = editor
      subscription = editor.onDidChangeModelContent(() => {
        onChange?.(editor.getValue())
      })
    })

    return () => {
      disposed = true
      subscription?.dispose?.()
      editorRef.current?.dispose?.()
    }
  }, [language, readOnly])

  return <div ref={containerRef} style={{ height, width }} className="monaco-editor" />
}
