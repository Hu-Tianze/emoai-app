import type { EmotionType } from '~/types';

export const EMOTIONS: Record<EmotionType, { color: string, name: string }> = {
  happy: { color: '#FFD700', name: 'Happy' },
  satisfied: { color: '#90EE90', name: 'Satisfied' },
  calm: { color: '#ADD8E6', name: 'Calm' },
  anxious: { color: '#FFA07A', name: 'Anxious' },
  angry: { color: '#FF6347', name: 'Angry' },
  sad: { color: '#6495ED', name: 'Sad' },
};

export const EMOTION_COLORS: Record<EmotionType, string> = Object.fromEntries(
  Object.entries(EMOTIONS).map(([k, v]) => [k, v.color]),
) as Record<EmotionType, string>;
