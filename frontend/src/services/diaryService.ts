import type { DiaryRecord } from '~/types';

const MOCK_DIARY_DATA: DiaryRecord[] = [
  {
    id: '1',
    date: '2025-10-18',
    characterId: 'maya',
    emotionScores: { happy: 8, satisfied: 7, calm: 6, anxious: 2, angry: 1, sad: 1 },
    moodKeywords: ['grateful', 'productive', 'calm'],
    moodSummary: 'Today was a good day. I felt productive and grateful for the small things.',
    trendAnalysis: 'Your mood has been steadily improving over the past week.',
    insights: 'You tend to feel happier on days when you spend time outdoors.',
    practice: 'Try to spend at least 15 minutes outside tomorrow.',
    message: 'Maya is proud of you for taking care of yourself.',
    createdAt: Date.now(),
  },
  {
    id: '2',
    date: '2025-10-17',
    characterId: 'atlas',
    emotionScores: { happy: 4, satisfied: 3, calm: 5, anxious: 6, angry: 2, sad: 5 },
    moodKeywords: ['tired', 'anxious', 'okay'],
    moodSummary: 'Felt a bit anxious today about the upcoming presentation.',
    trendAnalysis: 'Anxiety levels have been higher than usual.',
    insights: 'Your anxiety seems to be linked to work-related stress.',
    practice: 'Try some deep breathing exercises before your presentation.',
    message: 'Atlas reminds you that it is okay to feel anxious sometimes.',
    createdAt: Date.now() - 86400000,
  },
];

export const diaryService = {
  async getDiaryList(): Promise<DiaryRecord[]> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(MOCK_DIARY_DATA);
      }, 500);
    });
  },
  async getDiaryByDate(date: string): Promise<DiaryRecord | undefined> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(MOCK_DIARY_DATA.find(d => d.date === date));
      }, 500);
    });
  },
};
