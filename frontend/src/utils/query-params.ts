import { appConfig } from '@/app/config';
import type {
  MostRatedRankingRequest,
  SearchRequest,
  SubjectListRequest,
  TopScoreRankingRequest,
} from '@/types/api-requests';

export type RankingQueryRequest =
  | { readonly type: 'top_score'; readonly request: TopScoreRankingRequest }
  | { readonly type: 'most_rated'; readonly request: MostRatedRankingRequest };

function appendPagination(
  params: URLSearchParams,
  request: { readonly page: number; readonly pageSize: number },
): void {
  if (request.page !== appConfig.defaultPage) {
    params.set('page', String(request.page));
  }
  if (request.pageSize !== appConfig.defaultPageSize) {
    params.set('page_size', String(request.pageSize));
  }
}

export function buildSeasonQuery(request: SubjectListRequest): string {
  const params = new URLSearchParams();
  params.set('year', String(request.year));
  params.set('season', request.season);
  if (request.minTotal !== appConfig.defaultMinTotal) {
    params.set('min_total', String(request.minTotal));
  }
  appendPagination(params, request);
  return params.toString();
}

export function buildSearchQuery(request: SearchRequest): string {
  const params = new URLSearchParams();
  params.set('q', request.query);
  appendPagination(params, request);
  return params.toString();
}

export function buildRankingQuery({ type, request }: RankingQueryRequest): string {
  const params = new URLSearchParams();
  if (type === 'top_score' && request.minTotal !== appConfig.defaultMinTotal) {
    params.set('min_total', String(request.minTotal));
  }
  appendPagination(params, request);
  return params.toString();
}

export const buildSubjectListQuery = buildSeasonQuery;

export function buildTopScoreRankingQuery(request: TopScoreRankingRequest): string {
  return buildRankingQuery({ type: 'top_score', request });
}

export function buildMostRatedRankingQuery(request: MostRatedRankingRequest): string {
  return buildRankingQuery({ type: 'most_rated', request });
}
