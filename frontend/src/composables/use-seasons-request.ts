import type { SeasonListResponse } from '@/api/api-contract';
import { fetchSeasons } from '@/api/seasons-api';
import { useRequestState, type RequestState } from '@/composables/use-request-state';

export type SeasonsRequestState = RequestState<SeasonListResponse, undefined>;

export function useSeasonsRequest(): SeasonsRequestState {
  return useRequestState<SeasonListResponse, undefined>(
    (_input: undefined, signal: AbortSignal): Promise<SeasonListResponse> => fetchSeasons(signal),
  );
}
