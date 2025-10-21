export type EmotionType = 'happy' | 'satisfied' | 'calm' | 'anxious' | 'angry' | 'sad'

export interface EmotionScores {
  happy: number // 0-10
  satisfied: number // 0-10
  calm: number // 0-10
  anxious: number // 0-10
  angry: number // 0-10
  sad: number // 0-10
}

export interface EmotionAnalysis {
  primary: EmotionType
  secondary?: EmotionType
  scores: EmotionScores
  keywords: string[]
}
