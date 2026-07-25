import {
  MostRatedRankingResponseSchema,
  TopScoreRankingResponseSchema,
  type MostRatedRankingResponse,
  type TopScoreRankingResponse,
} from '@/api/api-contract';
import { getJson } from '@/api/http-client';
import type { MostRatedRankingRequest, TopScoreRankingRequest } from '@/types/api-requests';
import { buildMostRatedRankingQuery, buildTopScoreRankingQuery } from '@/utils/query-params';

export function fetchTopScoreRanking(
  request: TopScoreRankingRequest,
  signal?: AbortSignal,
): Promise<TopScoreRankingResponse> {
  return getJson(
    `/rankings/top-score?${buildTopScoreRankingQuery(request)}`,
    TopScoreRankingResponseSchema,
    signal,
  );
}

export function fetchMostRatedRanking(
  request: MostRatedRankingRequest,
  signal?: AbortSignal,
): Promise<MostRatedRankingResponse> {
  return getJson(
    `/rankings/most-rated?${buildMostRatedRankingQuery(request)}`,
    MostRatedRankingResponseSchema,
    signal,
  );
}
