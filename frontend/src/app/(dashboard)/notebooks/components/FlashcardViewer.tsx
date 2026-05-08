'use client'

import { useState } from 'react'
import { NoteResponse } from '@/lib/types/api'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { MoreVertical, Trash2, RotateCw, Lightbulb } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { getDateLocale } from '@/lib/utils/date-locale'
import { useTranslation } from '@/lib/hooks/use-translation'
import { useDeleteNote } from '@/lib/hooks/use-notes'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'

interface FlashcardViewerProps {
  flashcard: NoteResponse
  onDeleted?: () => void
}

export function FlashcardViewer({ flashcard, onDeleted }: FlashcardViewerProps) {
  const { t, language } = useTranslation()
  const [isFlipped, setIsFlipped] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)

  const deleteNote = useDeleteNote()

  // Parse flashcard content
  let question = ''
  let answer = ''
  try {
    const content = typeof flashcard.content === 'string'
      ? JSON.parse(flashcard.content)
      : flashcard.content
    question = content.question || ''
    answer = content.answer || ''
  } catch {
    question = flashcard.content || ''
  }

  const handleDeleteClick = () => {
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    try {
      await deleteNote.mutateAsync(flashcard.id)
      setDeleteDialogOpen(false)
      onDeleted?.()
    } catch (error) {
      console.error('Failed to delete flashcard:', error)
    }
  }

  return (
    <>
      <div className="perspective-1000 w-full">
        <div
          className={`relative w-full h-48 cursor-pointer transition-transform duration-500 transform-style-preserve-3d ${
            isFlipped ? 'rotate-y-180' : ''
          }`}
          onClick={() => setIsFlipped(!isFlipped)}
        >
          {/* Front - Question */}
          <div className="absolute inset-0 backface-hidden rounded-xl border bg-card p-4 flex flex-col shadow-md hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-primary/10 text-primary">
                  <Lightbulb className="h-3.5 w-3.5" />
                  <span className="text-xs font-medium">{t('common.question')}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground">
                  {formatDistanceToNow(new Date(flashcard.updated), {
                    addSuffix: true,
                    locale: getDateLocale(language)
                  })}
                </span>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 w-7 p-0 hover:bg-destructive/10"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-48">
                    <DropdownMenuItem
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeleteClick()
                      }}
                      className="text-red-600 focus:text-red-600"
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      {t('notebooks.deleteNote')}
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>
            <div className="flex-1 flex items-center justify-center text-center">
              <p className="text-base font-medium leading-relaxed">
                {question}
              </p>
            </div>
            <div className="flex items-center justify-center gap-1 text-xs text-muted-foreground mt-2">
              <RotateCw className="h-3 w-3" />
              <span>{t('studio.flipToAnswer')}</span>
            </div>
          </div>

          {/* Back - Answer */}
          <div className="absolute inset-0 backface-hidden rotate-y-180 rounded-xl border bg-primary/5 p-4 flex flex-col shadow-md">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-primary/20 text-primary">
                <span className="text-xs font-medium">{t('common.answer')}</span>
              </div>
            </div>
            <div className="flex-1 flex items-center justify-center text-center overflow-auto">
              <p className="text-sm text-muted-foreground leading-relaxed">
                {answer}
              </p>
            </div>
            <div className="flex items-center justify-center gap-1 text-xs text-muted-foreground mt-2">
              <RotateCw className="h-3 w-3" />
              <span>{t('studio.flipToQuestion')}</span>
            </div>
          </div>
        </div>
      </div>

      <ConfirmDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        title={t('notebooks.deleteNote')}
        description={t('notebooks.deleteNoteConfirm')}
        confirmText={t('common.delete')}
        onConfirm={handleDeleteConfirm}
        isLoading={deleteNote.isPending}
        confirmVariant="destructive"
      />
    </>
  )
}
