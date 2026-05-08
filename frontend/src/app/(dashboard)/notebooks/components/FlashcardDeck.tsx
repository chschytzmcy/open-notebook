'use client'

import { useState, useMemo } from 'react'
import { NoteResponse } from '@/lib/types/api'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { MoreVertical, Trash2, RotateCw, Lightbulb, ChevronLeft, ChevronRight } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { getDateLocale } from '@/lib/utils/date-locale'
import { useTranslation } from '@/lib/hooks/use-translation'
import { useDeleteNote } from '@/lib/hooks/use-notes'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { Loader2 } from 'lucide-react'

interface FlashcardDeckProps {
  notes: NoteResponse[]
  onDeleted?: () => void
}

interface FlashcardData {
  id: string
  question: string
  answer: string
  created: string
}

function parseFlashcard(note: NoteResponse): FlashcardData | null {
  try {
    const content = note.content
    let parsed: Record<string, unknown> = {}

    if (typeof content === 'string') {
      parsed = JSON.parse(content)
    } else if (typeof content === 'object' && content !== null) {
      parsed = content as Record<string, unknown>
    } else {
      return null
    }

    return {
      id: note.id,
      question: (parsed.question as string) || '',
      answer: (parsed.answer as string) || '',
      created: note.created,
    }
  } catch (e) {
    console.error('Failed to parse flashcard:', e, 'content:', note.content)
  }
  return null
}

export function FlashcardDeck({ notes, onDeleted }: FlashcardDeckProps) {
  const { t, language } = useTranslation()
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isFlipped, setIsFlipped] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)

  const deleteNote = useDeleteNote()

  // Parse all flashcards
  const flashcards = useMemo(() => {
    return notes
      .filter(note => note.note_type === 'flashcard')
      .map(parseFlashcard)
      .filter((f): f is FlashcardData => f !== null)
      .sort((a, b) => new Date(a.created).getTime() - new Date(b.created).getTime())
  }, [notes])

  const currentCard = flashcards[currentIndex]

  const handlePrev = () => {
    setIsFlipped(false)
    setCurrentIndex((prev) => (prev === 0 ? flashcards.length - 1 : prev - 1))
  }

  const handleNext = () => {
    setIsFlipped(false)
    setCurrentIndex((prev) => (prev === flashcards.length - 1 ? 0 : prev + 1))
  }

  const handleDeleteClick = () => {
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!currentCard) return
    try {
      await deleteNote.mutateAsync(currentCard.id)
      setDeleteDialogOpen(false)
      // If we deleted the last card, go back
      if (flashcards.length === 1) {
        onDeleted?.()
      } else if (currentIndex >= flashcards.length - 1) {
        setCurrentIndex(Math.max(0, currentIndex - 1))
      }
    } catch (error) {
      console.error('Failed to delete flashcard:', error)
    }
  }

  if (flashcards.length === 0) {
    return null
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Lightbulb className="h-4 w-4 text-primary" />
          <span>{t('studio.flashcards')}</span>
          <span className="text-xs">
            ({currentIndex + 1} / {flashcards.length})
          </span>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0 hover:bg-destructive/10">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuItem
              onClick={handleDeleteClick}
              className="text-red-600 focus:text-red-600"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              {t('notebooks.deleteNote')}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Flashcard */}
      <div className="perspective-1000 w-full">
        <div
          className={`relative w-full h-56 cursor-pointer transition-transform duration-500 transform-style-preserve-3d ${
            isFlipped ? 'rotate-y-180' : ''
          }`}
          onClick={() => setIsFlipped(!isFlipped)}
        >
          {/* Front - Question */}
          <div className="absolute inset-0 backface-hidden rounded-xl border bg-card p-4 flex flex-col shadow-md hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-primary/10 text-primary">
                <Lightbulb className="h-3.5 w-3.5" />
                <span className="text-xs font-medium">{t('common.question')}</span>
              </div>
              <span className="text-xs text-muted-foreground">
                {currentCard && formatDistanceToNow(new Date(currentCard.created), {
                  addSuffix: true,
                  locale: getDateLocale(language)
                })}
              </span>
            </div>
            <div className="flex-1 flex items-center justify-center text-center px-2">
              <p className="text-base font-medium leading-relaxed">
                {currentCard?.question || 'No question'}
              </p>
            </div>
            <div className="flex items-center justify-center gap-1 text-xs text-muted-foreground mt-2">
              <RotateCw className="h-3 w-3" />
              <span>{t('studio.flipToAnswer')}</span>
            </div>
          </div>

          {/* Back - Answer */}
          <div className="absolute inset-0 backface-hidden rotate-y-180 rounded-xl border bg-primary/5 p-4 flex flex-col shadow-md">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-primary/20 text-primary">
                <span className="text-xs font-medium">{t('common.answer')}</span>
              </div>
            </div>
            <div className="flex-1 flex items-center justify-center text-center px-2 overflow-auto">
              <p className="text-sm text-muted-foreground leading-relaxed">
                {currentCard?.answer || 'No answer'}
              </p>
            </div>
            <div className="flex items-center justify-center gap-1 text-xs text-muted-foreground mt-2">
              <RotateCw className="h-3 w-3" />
              <span>{t('studio.flipToQuestion')}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-center gap-4">
        <Button
          variant="outline"
          size="sm"
          onClick={handlePrev}
          disabled={deleteNote.isPending}
          className="gap-1"
        >
          <ChevronLeft className="h-4 w-4" />
          {t('studio.previousCard')}
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={handleNext}
          disabled={deleteNote.isPending}
          className="gap-1"
        >
          {t('studio.nextCard')}
          <ChevronRight className="h-4 w-4" />
        </Button>
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
    </div>
  )
}
