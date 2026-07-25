import type { MostRatedRankingResponse, TopScoreRankingResponse } from '@/api/api-contract';
import { fetchMostRatedRanking, fetchTopScoreRanking } from '@/api/rankings-api';
import { useRequestState, type RequestState } from '@/composables/use-request-state';
import type { MostRatedRankingRequest, TopScoreRankingRequest } from '@/types/api-requests';

export type RankingRequest =
  | { readonly type: 'top_score'; readonly request: TopScoreRankingRequest }
  | { readonly type: 'most_rated'; readonly request: MostRatedRankingRequest };
export type RankingResponse = TopScoreRankingResponse | MostRatedRankingResponse;
export type RankingRequestState = RequestState<RankingResponse, RankingRequest>;

export function useRankingRequest(): RankingRequestState {
  return useRequestState<RankingResponse, RankingRequest>(
    (input: RankingRequest, signal: AbortSignal): Promise<RankingResponse> => {
      if (input.type === 'top_score') {
        return fetchTopScoreRanking(input.request, signal);
      }
      return fetchMostRatedRanking(input.request, signal);
    },
  );
}
