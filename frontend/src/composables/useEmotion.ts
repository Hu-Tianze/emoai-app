import { ref, watch, type Ref } from 'vue';
import type { EmotionScores, ChatMessage } from '~/types';

const initialScores: EmotionScores = {
  happy: 0,
  satisfied: 0,
  calm: 0,
  anxious: 0,
  angry: 0,
  sad: 0,
};

export function useEmotion(messages: Ref<ChatMessage[]> | ChatMessage[]) {
  const emotionScores = ref<EmotionScores>({ ...initialScores });

  // Mock analysis: update emotions based on message count
  const messagesList = Array.isArray(messages) ? messages : messages.value;

  watch(
    () => messagesList,
    () => {
      const count = messagesList.length;
      emotionScores.value.happy = Math.min(10, count * 2);
      emotionScores.value.anxious = Math.max(0, 10 - count);
    },
  );

  return {
    emotionScores,
  };
}
