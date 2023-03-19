export const SCOPE_TO_LABEL = {
  user: 'General User',
  admin: 'Administrator',
} as const;

export type VersionResponse = {
  initialized: boolean;
  version: string;
};
