import { HomeResponseSchema, type HomeResponse } from '@/api/api-contract';
import { getJson } from '@/api/http-client';

export function fetchHome(signal?: AbortSignal): Promise<HomeResponse> {
  return getJson('/home', HomeResponseSchema, signal);
}
