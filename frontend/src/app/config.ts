import { z } from 'zod';

const apiBaseUrlSchema = z
  .string()
  .trim()
  .min(1, 'VITE_API_BASE_URL must not be empty.')
  .refine((value: string): boolean => value.startsWith('/') || /^https?:\/\//.test(value), {
    message: 'VITE_API_BASE_URL must be an absolute HTTP URL or a root-relative path.',
  });

function normalizeApiBaseUrl(value: string): string {
  return value.replace(/\/+$/, '') || '/';
}

const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? '/api';

export const appConfig = Object.freeze({
  apiBaseUrl: normalizeApiBaseUrl(apiBaseUrlSchema.parse(rawApiBaseUrl)),
});
