import * as monaco from 'monaco-editor'
import { useEffect, useRef, useState } from 'react'

export const MonacoEditor: React.FC<{
  defaultValue?: string
  onChange?: (value: string) => void
  height?: string
  width?: string
}> = ({ defaultValue, onChange, height = '100%', width = '100%' }) => {
  const [editor] = useState<monaco.editor.IStandaloneCodeEditor | null>(null)
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null)

  useEffect(() => {
    if (!editorRef.current) {
      editorRef.current = monaco.editor.create(document.createElement('div'), {
        value: defaultValue || '',
        language: 'python',
        theme: 'vs-dark',
        automaticLayout: true,
        minimap: {
          enabled: true
        }
      })
    }

    if (editorRef.current && defaultValue) {
      editorRef.current.setValue(defaultValue)
    }

    return () => {
      monaco.editor.dispose(editorRef.current)
    }
  }, [defaultValue])

  useEffect(() => {
    if (!editorRef.current) return
    const handleChange = (value: string) => {
      onChange?.(value)
    }
    editorRef.current.onDidChangeModelContent(handleChange)
    return () => {
      editorRef.current.offDidChangeModelContent(handleChange)
    }
  }, [onChange])

  useEffect(() => {
    if (editorRef.current) {
      editorRef.current.layout()
    }
  }, [height, width])

  return (
    <div
      ref={editorRef}
      style={{ height, width }}
      className="monaco-editor"
    />
  )
}