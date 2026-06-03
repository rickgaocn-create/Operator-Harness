export interface FeishuConfig {
  larkProfile: string;
  /**
   * Optional pre-bound chat. If set, replaces the access.json allowlist mechanism
   * with a single hardcoded chat — legacy single-user mode kept for backwards
   * compatibility with the env-based FEISHU_CHAT_ID config. New deployments
   * should leave this unset and use access.json instead.
   */
  chatId?: string;
  configFilePath?: string;
  startCommandHint?: string;
  /** Path to feishu-access.json. Defaults to ~/.afk-code/feishu-access.json. */
  accessFilePath?: string;
}
