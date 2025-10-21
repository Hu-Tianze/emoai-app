import type { EmotionScores } from './emotion';

export interface DiaryRecord {
  id: string
  date: string // YYYY-MM-DD
  characterId: string
  emotionScores: EmotionScores
  moodKeywords: [string, string, string]
  moodSummary: string
  trendAnalysis: string
  insights: string
  practice: string
  message: string
  createdAt: number
}
