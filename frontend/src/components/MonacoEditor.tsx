// @ts-nocheck
import * as monaco from 'monaco-editor'
import { useEffect, useRef, useState } from 'react'
import { useUserStore } from '@/stores/use-user-store'

export const MonacoEditor: React.FC<{
  defaultValue?: string
  onChange?: (value: string) => void
  height?: string
  width?: string
  readOnly?: boolean
  language?: string
}> = ({ defaultValue, onChange, height = '100%', width = '100%', readOnly = false, language = 'python' }) => {
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null)

  useEffect(() => {
    editorRef.current = monaco.editor.create(document.createElement('div'), {
      value: defaultValue || '',
      language,
      theme: 'vs-dark',
      automaticLayout: true,
      minimap: {
        enabled: true
      },
      readOnly
    })
  }, [defaultValue, language, readOnly])

  useEffect(() => {
    if (!editorRef.current) return
    const handleChange = (e: any) => {
      onChange?.(editorRef.current.getValue())
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