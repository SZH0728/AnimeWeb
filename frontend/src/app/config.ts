import { z } from 'zod';

// 未设置 VITE_DEFAULT_PAGE 时使用的默认页码。
export const DEFAULT_PAGE = 1;
// 未设置 VITE_DEFAULT_PAGE_SIZE 时使用的默认每页条目数。
export const DEFAULT_PAGE_SIZE = 20;
// 未设置 VITE_DEFAULT_MIN_TOTAL 时使用的默认最低评价人数。
export const DEFAULT_MIN_TOTAL = 0;
// 未设置 VITE_API_BASE_URL 时使用的默认 API 路径。
export const DEFAULT_API_ROUTE = '/api';

const apiBaseUrlSchema = z
  .string()
  .trim()
  .min(1, 'VITE_API_BASE_URL must not be empty.')
  .refine((value: string): boolean => value.startsWith('/') || /^https?:\/\//.test(value), {
    message: 'VITE_API_BASE_URL must be an absolute HTTP URL or a root-relative path.',
  });

function createIntegerSchema(variableName: string, minimum: number, maximum: number) {
  return z
    .string()
    .regex(/^\d+$/, `${variableName} must be a non-negative decimal integer.`)
    .transform(Number)
    .refine(Number.isSafeInteger, `${variableName} must be a safe integer.`)
    .refine((value: number): boolean => value >= minimum && value <= maximum, {
      message: `${variableName} must be between ${minimum} and ${maximum}.`,
    });
}

const defaultPageSchema = createIntegerSchema('VITE_DEFAULT_PAGE', 1, Number.MAX_SAFE_INTEGER);
const defaultPageSizeSchema = createIntegerSchema('VITE_DEFAULT_PAGE_SIZE', 1, 100);
const defaultMinTotalSchema = createIntegerSchema(
  'VITE_DEFAULT_MIN_TOTAL',
  0,
  Number.MAX_SAFE_INTEGER,
);

function normalizeApiBaseUrl(value: string): string {
  return value.replace(/\/+$/, '') || '/';
}

const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? String(DEFAULT_API_ROUTE);
const rawDefaultPage = import.meta.env.VITE_DEFAULT_PAGE ?? String(DEFAULT_PAGE);
const rawDefaultPageSize = import.meta.env.VITE_DEFAULT_PAGE_SIZE ?? String(DEFAULT_PAGE_SIZE);
const rawDefaultMinTotal = import.meta.env.VITE_DEFAULT_MIN_TOTAL ?? String(DEFAULT_MIN_TOTAL);

export const appConfig = Object.freeze({
  apiBaseUrl: normalizeApiBaseUrl(apiBaseUrlSchema.parse(rawApiBaseUrl)),
  defaultPage: defaultPageSchema.parse(rawDefaultPage),
  defaultPageSize: defaultPageSizeSchema.parse(rawDefaultPageSize),
  defaultMinTotal: defaultMinTotalSchema.parse(rawDefaultMinTotal),
});
