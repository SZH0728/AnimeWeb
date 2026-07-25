import type { z } from 'zod';

import { appConfig } from '@/app/config';
import { ApiError, NetworkError, ResponseContractError, isRequestCancelled } from '@/api/api-error';
import { ApiErrorResponseSchema } from '@/api/api-contract';

function buildRequestUrl(path: string): string {
  const baseUrl = appConfig.apiBaseUrl;
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return baseUrl === '/' ? normalizedPath : `${baseUrl}${normalizedPath}`;
}

async function parseJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch (error: unknown) {
    throw new ResponseContractError('API 响应不是有效 JSON。', error);
  }
}

export async function getJson<T>(
  path: string,
  successSchema: z.ZodType<T>,
  signal?: AbortSignal,
): Promise<T> {
  let response: Response;

  try {
    response = await fetch(buildRequestUrl(path), {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal,
    });
  } catch (error: unknown) {
    if (isRequestCancelled(error)) {
      throw error;
    }
    throw new NetworkError(error);
  }

  const payload = await parseJson(response);

  if (response.ok) {
    const result = successSchema.safeParse(payload);
    if (result.success) {
      return result.data;
    }
    throw new ResponseContractError('API 成功响应不符合约定。', result.error);
  }

  const result = ApiErrorResponseSchema.safeParse(payload);
  if (result.success) {
    throw new ApiError(response.status, result.data.error.code, result.data.error.message);
  }
  throw new ResponseContractError('API 错误响应不符合约定。', result.error);
}
