import type { SeasonName } from '@/api/api-contract';

export interface PaginationRequest {
  readonly page: number;
  readonly pageSize: number;
}

export interface SubjectListRequest extends PaginationRequest {
  readonly year: number;
  readonly season: SeasonName;
  readonly minTotal: number;
}

export interface SearchRequest extends PaginationRequest {
  readonly query: string;
}

export interface TopScoreRankingRequest extends PaginationRequest {
  readonly minTotal: number;
}

export type MostRatedRankingRequest = PaginationRequest;
export type RankingType = 'top_score' | 'most_rated';
export type BgmId = number;
