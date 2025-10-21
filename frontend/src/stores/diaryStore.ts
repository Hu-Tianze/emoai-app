import { defineStore } from 'pinia';
import type { DiaryRecord } from '~/types';

export const useDiaryStore = defineStore('diary', {
  state: () => ({
    diaryEntries: [] as DiaryRecord[],
  }),
  actions: {
    setDiaryEntries(entries: DiaryRecord[]) {
      this.diaryEntries = entries;
    },
  },
});
