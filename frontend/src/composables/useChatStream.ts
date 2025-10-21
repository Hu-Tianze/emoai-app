import { ref } from 'vue';
import { useChatStore } from '~/stores/chatStore';
import { aiService } from '~/services/aiService';
import type { ChatMessage } from '~/types';

export function useChatStream(characterId: string) {
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
    newMessage.value = '';

    const stream = await aiService.getResponseStream(store.messages);
    // reader value may be `string` or binary (Uint8Array / ArrayBuffer) depending on implementation
    const reader: ReadableStreamDefaultReader<unknown>
      = (stream as ReadableStream).getReader();

    const aiMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'assistant',
      characterId,
      content: '',
      timestamp: Date.now(),
    };
    store.addMessage(aiMessage);

    const decoder = new TextDecoder();
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        let chunk = '';
        if (typeof value === 'string') {
          chunk = value;
        } else if (value instanceof Uint8Array) {
          chunk = decoder.decode(value);
        } else if (value instanceof ArrayBuffer) {
          chunk = decoder.decode(new Uint8Array(value));
        } else {
          // fallback
          chunk = String(value);
        }

        aiMessage.content += chunk;
      }
    } catch (err) {
      // on stream error, append an error indicator
      aiMessage.content += '\n\n[Stream error]';
      // optional: you could also log or push a separate error message
      console.error('Stream error', err);
    }
  };

  return {
    messages: store.messages,
    newMessage,
    sendMessage,
  };
}
