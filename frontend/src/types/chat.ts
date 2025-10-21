export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  characterId: string
  content: string
  timestamp: number
}
