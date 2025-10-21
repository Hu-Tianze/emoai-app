import type { ChatMessage } from '~/types';

// This is a mock AI service. In a real application, this would make API calls to a backend.
export const aiService = {
  async getResponse(messages: ChatMessage[]): Promise<string> {
    const lastMessage = messages[messages.length - 1]?.content || '';
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(`This is a mock response to: "${lastMessage}"`);
      }, 1000);
    });
  },

  async getResponseStream(messages: ChatMessage[]): Promise<ReadableStream<string>> {
    const lastMessage = messages[messages.length - 1]?.content || '';
    const responseChunks = [
      'This ',
      'is ',
      'a ',
      'mock ',
      'streamed ',
      'response ',
      'to: ',
      `"${lastMessage}"`,
    ];

    return new ReadableStream({
      async start(controller) {
        for (const chunk of responseChunks) {
          controller.enqueue(chunk);
          await new Promise(r => setTimeout(r, 100));
        }
        controller.close();
      },
    });
  },
};
