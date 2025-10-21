export function handleError(error: unknown, context: string = 'Unknown') {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`[${context}] Error:`, message);
  // In a real app, you might send this to a logging service
}
