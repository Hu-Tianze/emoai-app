import { useDiaryStore } from '~/stores/diaryStore';
import { diaryService } from '~/services/diaryService';

export function useDiaryList() {
  const store = useDiaryStore();

  const fetchDiaryList = async () => {
    const entries = await diaryService.getDiaryList();
    store.setDiaryEntries(entries);
  };

  return {
    diaryEntries: store.diaryEntries,
    fetchDiaryList,
  };
}
