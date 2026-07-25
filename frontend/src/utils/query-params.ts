import type {
  MostRatedRankingRequest,
  SearchRequest,
  SubjectListRequest,
  TopScoreRankingRequest,
} from '@/types/api-requests';

function appendPagination(
  params: URLSearchParams,
  request: { readonly page: number; readonly pageSize: number },
): void {
  params.set('page', String(request.page));
  params.set('page_size', String(request.pageSize));
}

export function buildSubjectListQuery(request: SubjectListRequest): string {
  const params = new URLSearchParams();
  params.set('year', String(request.year));
  params.set('season', request.season);
  params.set('min_total', String(request.minTotal));
  appendPagination(params, request);
  return params.toString();
}

export function buildSearchQuery(request: SearchRequest): string {
  const params = new URLSearchParams();
  params.set('q', request.query);
  appendPagination(params, request);
  return params.toString();
}

export function buildTopScoreRankingQuery(request: TopScoreRankingRequest): string {
  const params = new URLSearchParams();
  params.set('min_total', String(request.minTotal));
  appendPagination(params, request);
  return params.toString();
}

export function buildMostRatedRankingQuery(request: MostRatedRankingRequest): string {
  const params = new URLSearchParams();
  appendPagination(params, request);
  return params.toString();
}
