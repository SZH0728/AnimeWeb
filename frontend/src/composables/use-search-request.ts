import type { SearchResponse } from '@/api/api-contract';
import { searchSubjects } from '@/api/search-api';
import { useRequestState, type RequestState } from '@/composables/use-request-state';
import type { SearchRequest } from '@/types/api-requests';

export type SearchRequestState = RequestState<SearchResponse, SearchRequest>;

export function useSearchRequest(): SearchRequestState {
  return useRequestState(searchSubjects);
}
