import { useMutation, useQueryClient } from '@tanstack/react-query'
import { studioApi } from '@/lib/api/studio'
import { useToast } from '@/lib/hooks/use-toast'
import { useTranslation } from '@/lib/hooks/use-translation'
import { getApiErrorKey } from '@/lib/utils/error-handler'
import { QUERY_KEYS } from '@/lib/api/query-client'

export function useGenerateFlashcards() {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const { t } = useTranslation()

  return useMutation({
    mutationFn: (notebookId: string) => studioApi.generateFlashcards(notebookId),
    onSuccess: (_, notebookId) => {
      // Invalidate notes to refresh NotesColumn
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.notes(notebookId) })
      toast({
        title: t('common.success'),
        description: t('studio.flashcardGeneratedSuccess'),
      })
    },
    onError: (error: unknown) => {
      toast({
        title: t('common.error'),
        description: getApiErrorKey(error, t('common.failedToGenerate')),
        variant: 'destructive',
      })
    },
  })
}

export function useGenerateMindMap() {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const { t } = useTranslation()

  return useMutation({
    mutationFn: (notebookId: string) => studioApi.generateMindMap(notebookId),
    onSuccess: (_, notebookId) => {
      // Invalidate notes to refresh NotesColumn
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.notes(notebookId) })
      toast({
        title: t('common.success'),
        description: t('studio.mindMapGeneratedSuccess'),
      })
    },
    onError: (error: unknown) => {
      toast({
        title: t('common.error'),
        description: getApiErrorKey(error, t('common.failedToGenerate')),
        variant: 'destructive',
      })
    },
  })
}