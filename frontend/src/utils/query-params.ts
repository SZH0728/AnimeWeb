import { appConfig } from '@/app/config';
import type {
  MostRatedRankingRequest,
  RankingType,
  SearchRequest,
  SubjectListRequest,
  TopScoreRankingRequest,
} from '@/types/api-requests';

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

export function buildRankingQuery(
  rankingType: RankingType,
  request: TopScoreRankingRequest | MostRatedRankingRequest,
): string {
  const params = new URLSearchParams();
  if (rankingType === 'top_score') {
    const topScoreRequest = request as TopScoreRankingRequest;
    if (topScoreRequest.minTotal !== appConfig.defaultMinTotal) {
      params.set('min_total', String(topScoreRequest.minTotal));
    }
  }
  appendPagination(params, request);
  return params.toString();
}

export const buildSubjectListQuery = buildSeasonQuery;

export function buildTopScoreRankingQuery(request: TopScoreRankingRequest): string {
  return buildRankingQuery('top_score', request);
}

export function buildMostRatedRankingQuery(request: MostRatedRankingRequest): string {
  return buildRankingQuery('most_rated', request);
}
