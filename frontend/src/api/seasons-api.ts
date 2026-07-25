import { SeasonListResponseSchema, type SeasonListResponse } from '@/api/api-contract';
import { getJson } from '@/api/http-client';

export function fetchSeasons(signal?: AbortSignal): Promise<SeasonListResponse> {
  return getJson('/seasons', SeasonListResponseSchema, signal);
}
