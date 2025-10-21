import { ref } from 'vue';
import { useChatStore } from '~/stores/chatStore';
import { aiService } from '~/services/aiService';
import type { ChatMessage } from '~/types';

export function useChat(characterId: string) {
  const store = useChatStore();
  const newMessage = ref('');

  const sendMessage = async () => {
    if (!newMessage.value.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      characterId,
      content: newMessage.value,
      timestamp: Date.now(),
    };
    store.addMessage(userMessage);

    const aiResponse = await aiService.getResponse(store.messages);

    const aiMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'assistant',
      characterId,
      content: aiResponse,
      timestamp: Date.now(),
    };
    store.addMessage(aiMessage);

    newMessage.value = '';
  };

  return {
    messages: store.messages,
    newMessage,
    sendMessage,
  };
}
