import { buildPostSendArgs, parseMarkdownToRows, plainTextToRows } from './rich-message.js';

export type FeishuTranscriptBackend = 'claude' | 'codex';
export const FEISHU_MAX_MESSAGE_LENGTH = 4000;
export const FEISHU_HISTORY_PAGE_SIZE = 50;

/**
 * Build args to send a markdown-rich reply. Routes through Feishu `post`
 * (built by our own parser — see rich-message.ts for why we bypass lark-cli
 * `--markdown`). Plain text and markdown both go through this path; the parser
 * preserves blank lines and single line breaks as separate rows.
 */
export function buildFeishuMarkdownSendArgs(chatId: string, markdown: string, replyTo?: string): string[] {
  return buildPostSendArgs({ chatId, rows: parseMarkdownToRows(markdown), replyTo });
}

/**
 * Build args to send a plain-text reply (no markdown parsing — every line
 * becomes a row verbatim). Used for system notices where we don't want
 * surprise formatting if the text happens to contain markdown chars.
 */
export function buildFeishuTextSendArgs(chatId: string, text: string, replyTo?: string): string[] {
  return buildPostSendArgs({ chatId, rows: plainTextToRows(text), replyTo });
}

export function stripLeadingAssistantLabel(text: string): string {
  return text.replace(/^(?:Codex|Claude(?: Code)?)\s*:\s*(?:\r?\n)?/i, '');
}

export function buildFeishuHistoryListArgs(chatId: string): string[] {
  return [
    'im', '+chat-messages-list',
    '--as', 'bot',
    '--chat-id', chatId,
    '--page-size', String(FEISHU_HISTORY_PAGE_SIZE),
    '--sort', 'desc',
    '--format', 'json',
  ];
}

export function feishuHistoryMessageToReceiveEvent(message: any): any | null {
  if (!message || message.deleted === true) return null;
  if (message.sender?.sender_type !== 'user') return null;

  const messageId = typeof message.message_id === 'string' ? message.message_id : '';
  const chatId = typeof message.chat_id === 'string' ? message.chat_id : '';
  const senderId = typeof message.sender?.id === 'string' ? message.sender.id : '';
  if (!messageId || !chatId || !senderId) return null;

  return {
    chat_id: chatId,
    chat_type: 'p2p',
    content: typeof message.content === 'string' ? message.content : '',
    create_time: message.create_time ?? '',
    id: messageId,
    message_id: messageId,
    message_position: message.message_position,
    message_type: message.msg_type || message.message_type || 'text',
    sender_id: senderId,
    timestamp: message.create_time ?? '',
    type: 'im.message.receive_v1',
  };
}
