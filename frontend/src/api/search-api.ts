import { SearchResponseSchema, type SearchResponse } from '@/api/api-contract';
import { getJson } from '@/api/http-client';
import type { SearchRequest } from '@/types/api-requests';
import { buildSearchQuery } from '@/utils/query-params';

export function searchSubjects(
  request: SearchRequest,
  signal?: AbortSignal,
): Promise<SearchResponse> {
  return getJson(`/search?${buildSearchQuery(request)}`, SearchResponseSchema, signal);
}
