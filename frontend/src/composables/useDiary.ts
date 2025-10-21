import { ref } from 'vue';
import { diaryService } from '~/services/diaryService';
import type { DiaryRecord } from '~/types';

export function useDiary(date: string) {
  const diaryEntry = ref<DiaryRecord | null>(null);

  const fetchDiary = async () => {
    const entry = await diaryService.getDiaryByDate(date);
    diaryEntry.value = entry || null;
  };

  return {
    diaryEntry,
    fetchDiary,
  };
}
