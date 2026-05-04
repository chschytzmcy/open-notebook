'use client'

import dynamic from 'next/dynamic'
import { forwardRef, useEffect, useState } from 'react'

const MDEditor = dynamic(
  () => import('@uiw/react-md-editor').then((mod) => mod.default),
  { ssr: false }
)

export interface MarkdownEditorProps {
  value?: string
  onChange?: (value?: string) => void
  placeholder?: string
  height?: number
  preview?: 'live' | 'edit' | 'preview'
  hideToolbar?: boolean
  textareaId?: string
  name?: string
  className?: string
}

export const MarkdownEditor = forwardRef<HTMLDivElement, MarkdownEditorProps>(
  ({ value = '', onChange, placeholder, height = 300, preview = 'live', hideToolbar = false, className, textareaId, name }, ref) => {
    const [colorMode, setColorMode] = useState<'light' | 'dark'>('light')

    useEffect(() => {
      // 检测当前主题模式
      const checkTheme = () => {
        const isDark = document.documentElement.classList.contains('dark') ||
          window.matchMedia('(prefers-color-scheme: dark)').matches
        setColorMode(isDark ? 'dark' : 'light')
      }

      checkTheme()

      // 监听主题变化
      const observer = new MutationObserver(checkTheme)
      observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['class']
      })

      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      mediaQuery.addEventListener('change', checkTheme)

      return () => {
        observer.disconnect()
        mediaQuery.removeEventListener('change', checkTheme)
      }
    }, [])

    return (
      <div className={className} ref={ref}>
        <MDEditor
          value={value}
          onChange={onChange}
          preview={preview}
          height={height}
          hideToolbar={hideToolbar}
          textareaProps={{
            placeholder: placeholder || 'Enter markdown...',
            id: textareaId,
            name: name,
          }}
          data-color-mode={colorMode}
          style={{
            borderRadius: '0.5rem',
          }}
        />
      </div>
    )
  }
)

MarkdownEditor.displayName = 'MarkdownEditor'