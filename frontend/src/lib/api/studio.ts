import apiClient from './client'
import { FlashcardResponse, MindMapResponse } from '@/lib/types/api'

export const studioApi = {
  // Generate flashcard note - creates Note with note_type="flashcard"
  generateFlashcards: async (notebookId: string) => {
    const response = await apiClient.post<FlashcardResponse[]>(
      `/notebooks/${notebookId}/notes/generate-studio?note_type=flashcard`,
      {}
    )
    return response.data
  },

  // Generate mindmap note - creates Note with note_type="mindmap"
  generateMindMap: async (notebookId: string) => {
    const response = await apiClient.post<MindMapResponse>(
      `/notebooks/${notebookId}/notes/generate-studio?note_type=mindmap`,
      {}
    )
    return response.data
  },
}