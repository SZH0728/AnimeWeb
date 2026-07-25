import type { RatingHistoryResponse } from '@/api/api-contract';
import { fetchRatingHistory } from '@/api/subjects-api';
import { useRequestState, type RequestState } from '@/composables/use-request-state';
import type { BgmId } from '@/types/api-requests';

export type RatingHistoryRequestState = RequestState<RatingHistoryResponse, BgmId>;

export function useRatingHistoryRequest(): RatingHistoryRequestState {
  return useRequestState(fetchRatingHistory);
}
