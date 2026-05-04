'use client'

import { Controller, useForm, useWatch } from 'react-hook-form'
import { useEffect, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Dialog, DialogContent, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { useCreateNote, useUpdateNote, useNote } from '@/lib/hooks/use-notes'
import { QUERY_KEYS } from '@/lib/api/query-client'
import { MarkdownEditor } from '@/components/ui/markdown-editor'
import { InlineEdit } from '@/components/common/InlineEdit'
import { cn } from "@/lib/utils"
import { useTranslation } from '@/lib/hooks/use-translation'
import { Eye, Edit3 } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const createNoteSchema = z.object({
  title: z.string().optional(),
  content: z.string().min(1, 'Content is required'),
})

type CreateNoteFormData = z.infer<typeof createNoteSchema>

interface NoteEditorDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  notebookId: string
  note?: { id: string; title: string | null; content: string | null; note_type?: string | null }
}

export function NoteEditorDialog({ open, onOpenChange, notebookId, note }: NoteEditorDialogProps) {
  const { t } = useTranslation()
  const createNote = useCreateNote()
  const updateNote = useUpdateNote()
  const queryClient = useQueryClient()
  const isEditing = Boolean(note)
  const [viewMode, setViewMode] = useState<'edit' | 'preview'>('edit')

  // Ensure note ID has 'note:' prefix for API calls
  const noteIdWithPrefix = note?.id
    ? (note.id.includes(':') ? note.id : `note:${note.id}`)
    : ''

  const { data: fetchedNote, isLoading: noteLoading } = useNote(noteIdWithPrefix, { enabled: open && !!note?.id })
  const isSaving = isEditing ? updateNote.isPending : createNote.isPending
  const {
    handleSubmit,
    control,
    formState: { errors },
    reset,
    setValue,
  } = useForm<CreateNoteFormData>({
    resolver: zodResolver(createNoteSchema),
    defaultValues: {
      title: '',
      content: '',
    },
  })
  const watchTitle = useWatch({ control, name: 'title' })
  const watchContent = useWatch({ control, name: 'content' })
  const [isEditorFullscreen, setIsEditorFullscreen] = useState(false)

  useEffect(() => {
    if (!open) {
      reset({ title: '', content: '' })
      setViewMode('edit')
      return
    }

    const source = fetchedNote ?? note
    const title = source?.title ?? ''
    const content = source?.content ?? ''

    reset({ title, content })
  }, [open, note, fetchedNote, reset])

  useEffect(() => {
    if (!open) return

    const observer = new MutationObserver(() => {
      setIsEditorFullscreen(!!document.querySelector('.w-md-editor-fullscreen'))
    })
    observer.observe(document.body, { subtree: true, attributes: true, attributeFilter: ['class'] })
    return () => observer.disconnect()
  }, [open])

  const onSubmit = async (data: CreateNoteFormData) => {
    if (note) {
      await updateNote.mutateAsync({
        id: noteIdWithPrefix,
        data: {
          title: data.title || undefined,
          content: data.content,
        },
      })
      // Only invalidate notebook-specific queries if we have a notebookId
      if (notebookId) {
        queryClient.invalidateQueries({ queryKey: QUERY_KEYS.notes(notebookId) })
      }
    } else {
      // Creating a note requires a notebookId
      if (!notebookId) {
        console.error('Cannot create note without notebook_id')
        return
      }
      await createNote.mutateAsync({
        title: data.title || undefined,
        content: data.content,
        note_type: 'human',
        notebook_id: notebookId,
      })
    }
    reset()
    onOpenChange(false)
  }

  const handleClose = () => {
    reset()
    setIsEditorFullscreen(false)
    setViewMode('edit')
    onOpenChange(false)
  }

  const toggleViewMode = () => {
    setViewMode(prev => prev === 'edit' ? 'preview' : 'edit')
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className={cn(
          "sm:max-w-4xl w-full max-h-[90vh] overflow-hidden p-0 gap-0",
          isEditorFullscreen && "!max-w-screen !max-h-screen border-none w-screen h-screen"
      )}>
        <DialogTitle className="sr-only">
          {isEditing ? t('sources.editNote') : t('sources.createNote')}
        </DialogTitle>

        {/* Header */}
        <div className="border-b bg-muted/30 px-6 py-4 flex-shrink-0">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3 min-w-0 flex-1">
              {note?.note_type === 'ai' && (
                <Badge variant="secondary" className="shrink-0">
                  {t('common.aiGenerated')}
                </Badge>
              )}
              <InlineEdit
                id="note-title"
                name="title"
                value={watchTitle ?? ''}
                onSave={(value) => setValue('title', value || '')}
                placeholder={t('sources.addTitle')}
                emptyText={t('sources.untitledNote')}
                className="text-xl font-semibold truncate"
                inputClassName="text-xl font-semibold"
              />
            </div>

            <div className="flex items-center gap-2 shrink-0">
              {/* View mode toggle */}
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleViewMode}
                className="gap-2"
              >
                {viewMode === 'edit' ? (
                  <>
                    <Eye className="h-4 w-4" />
                    {t('common.preview')}
                  </>
                ) : (
                  <>
                    <Edit3 className="h-4 w-4" />
                    {t('common.edit')}
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex flex-col min-h-0">
          {isEditing && noteLoading ? (
            <div className="flex-1 flex items-center justify-center py-10">
              <span className="text-sm text-muted-foreground">{t('common.loading')}</span>
            </div>
          ) : (
            <div className={cn(
                "flex-1 overflow-y-auto",
                !isEditorFullscreen && "px-6 py-4")
            }>
              {viewMode === 'preview' ? (
                /* Preview mode - rendered markdown */
                <div className="prose prose-sm dark:prose-invert max-w-none min-h-[400px] max-h-[500px] overflow-y-auto text-sm leading-relaxed p-1">
                  {watchContent ? (
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        h1: ({ children }) => <h1 className="text-xl font-bold mb-4 mt-6">{children}</h1>,
                        h2: ({ children }) => <h2 className="text-lg font-semibold mb-3 mt-5">{children}</h2>,
                        h3: ({ children }) => <h3 className="text-base font-semibold mb-2 mt-4">{children}</h3>,
                        p: ({ children }) => <p className="mb-3 last:mb-0">{children}</p>,
                        ul: ({ children }) => <ul className="list-disc pl-4 mb-3">{children}</ul>,
                        ol: ({ children }) => <ol className="list-decimal pl-4 mb-3">{children}</ol>,
                        li: ({ children }) => <li className="mb-1">{children}</li>,
                        code: ({ children, className }) => {
                          const isInline = !className
                          return isInline
                            ? <code className="bg-muted px-1.5 py-0.5 rounded text-xs">{children}</code>
                            : <code className={cn("block bg-muted p-3 rounded-lg text-xs overflow-x-auto", className)}>{children}</code>
                        },
                        blockquote: ({ children }) => <blockquote className="border-l-4 border-primary/50 pl-4 italic text-muted-foreground">{children}</blockquote>,
                        a: ({ children, href }) => <a href={href} className="text-primary underline hover:no-underline">{children}</a>,
                        strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                        em: ({ children }) => <em className="italic">{children}</em>,
                        table: ({ children }) => (
                          <div className="my-4 overflow-x-auto">
                            <table className="min-w-full border-collapse border border-border">{children}</table>
                          </div>
                        ),
                        thead: ({ children }) => <thead className="bg-muted">{children}</thead>,
                        tbody: ({ children }) => <tbody>{children}</tbody>,
                        tr: ({ children }) => <tr className="border-b border-border">{children}</tr>,
                        th: ({ children }) => <th className="border border-border px-3 py-2 text-left font-semibold">{children}</th>,
                        td: ({ children }) => <td className="border border-border px-3 py-2">{children}</td>,
                      }}
                    >
                      {watchContent}
                    </ReactMarkdown>
                  ) : (
                    <p className="text-muted-foreground italic">
                      {t('sources.writeNotePlaceholder')}
                    </p>
                  )}
                </div>
              ) : (
                /* Edit mode */
                <Controller
                  control={control}
                  name="content"
                  render={({ field }) => (
                    <MarkdownEditor
                      key={note?.id ?? 'new'}
                      textareaId="note-content"
                      value={field.value}
                      onChange={field.onChange}
                      height={isEditorFullscreen ? 600 : 450}
                      placeholder={t('sources.writeNotePlaceholder')}
                      preview="live"
                      className={cn(
                          "w-full h-full [&_.w-md-editor]:!static [&_.w-md-editor]:!w-full [&_.w-md-editor-content]:overflow-y-auto",
                          !isEditorFullscreen && "rounded-lg border shadow-sm"
                      )}
                    />
                  )}
                />
              )}
              {errors.content && viewMode === 'edit' && (
                <p className="text-sm text-red-600 mt-2">{errors.content.message}</p>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t bg-muted/30 px-6 py-4 flex-shrink-0">
          <div className="flex justify-between items-center">
            <div className="text-xs text-muted-foreground">
              {isEditing ? t('sources.editNote') : t('sources.createNote')}
            </div>
            <div className="flex gap-2">
              <Button type="button" variant="outline" onClick={handleClose}>
                {t('common.cancel')}
              </Button>
              <Button
                type="submit"
                disabled={isSaving || (isEditing && noteLoading)}
                onClick={handleSubmit(onSubmit)}
              >
                {isSaving
                  ? isEditing ? `${t('common.saving')}...` : `${t('common.creating')}...`
                  : isEditing
                    ? t('sources.saveNote')
                    : t('sources.createNoteBtn')}
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
