import { appConfig } from '@/app/config';
import type { SeasonName } from '@/api/api-contract';
import type {
  BgmId,
  MostRatedRankingRequest,
  RankingType,
  SearchRequest,
  SubjectListRequest,
  TopScoreRankingRequest,
} from '@/types/api-requests';

export type RawRouteValue = string | null | readonly (string | null)[] | undefined;
export type RawRouteValues = Readonly<Record<string, RawRouteValue>>;

export type RouteParameterError =
  | 'invalid-year'
  | 'invalid-season'
  | 'incomplete-season-selection'
  | 'invalid-min-total'
  | 'invalid-page'
  | 'invalid-page-size'
  | 'invalid-query'
  | 'invalid-bgm-id'
  | 'unsupported-ranking-parameter';

export type ParsedRoute<T> =
  | { readonly status: 'valid'; readonly value: T }
  | { readonly status: 'invalid'; readonly reason: RouteParameterError };

export type ParsedSeasonCatalogRoute =
  | ParsedRoute<SubjectListRequest>
  | {
      readonly status: 'selection-required';
      readonly value: Readonly<Pick<SubjectListRequest, 'minTotal' | 'page' | 'pageSize'>>;
    };

function getScalarValue(query: RawRouteValues, key: string): string | undefined {
  const value = query[key];
  return typeof value === 'string' ? value : undefined;
}

function hasInvalidScalarValue(query: RawRouteValues, key: string): boolean {
  const value = query[key];
  return value !== undefined && typeof value !== 'string';
}

function parseInteger(value: string, minimum: number, maximum: number): number | undefined {
  if (!/^\d+$/.test(value)) {
    return undefined;
  }

  const numberValue = Number(value);
  if (!Number.isSafeInteger(numberValue) || numberValue < minimum || numberValue > maximum) {
    return undefined;
  }

  return numberValue;
}

function parsePagination(
  query: RawRouteValues,
): ParsedRoute<Readonly<{ page: number; pageSize: number }>> {
  if (hasInvalidScalarValue(query, 'page')) {
    return { status: 'invalid', reason: 'invalid-page' };
  }
  if (hasInvalidScalarValue(query, 'page_size')) {
    return { status: 'invalid', reason: 'invalid-page-size' };
  }

  const rawPage = getScalarValue(query, 'page');
  const rawPageSize = getScalarValue(query, 'page_size');
  const page =
    rawPage === undefined
      ? appConfig.defaultPage
      : parseInteger(rawPage, 1, Number.MAX_SAFE_INTEGER);
  const pageSize =
    rawPageSize === undefined ? appConfig.defaultPageSize : parseInteger(rawPageSize, 1, 100);

  if (page === undefined) {
    return { status: 'invalid', reason: 'invalid-page' };
  }
  if (pageSize === undefined) {
    return { status: 'invalid', reason: 'invalid-page-size' };
  }

  return { status: 'valid', value: { page, pageSize } };
}

function parseMinTotal(query: RawRouteValues): ParsedRoute<number> {
  if (hasInvalidScalarValue(query, 'min_total')) {
    return { status: 'invalid', reason: 'invalid-min-total' };
  }

  const rawMinTotal = getScalarValue(query, 'min_total');
  const minTotal =
    rawMinTotal === undefined
      ? appConfig.defaultMinTotal
      : parseInteger(rawMinTotal, 0, Number.MAX_SAFE_INTEGER);

  return minTotal === undefined
    ? { status: 'invalid', reason: 'invalid-min-total' }
    : { status: 'valid', value: minTotal };
}

export function parseSeasonCatalogRoute(query: RawRouteValues): ParsedSeasonCatalogRoute {
  const pagination = parsePagination(query);
  if (pagination.status === 'invalid') {
    return pagination;
  }

  const minTotal = parseMinTotal(query);
  if (minTotal.status === 'invalid') {
    return minTotal;
  }

  if (hasInvalidScalarValue(query, 'year')) {
    return { status: 'invalid', reason: 'invalid-year' };
  }
  if (hasInvalidScalarValue(query, 'season')) {
    return { status: 'invalid', reason: 'invalid-season' };
  }

  const rawYear = getScalarValue(query, 'year');
  const rawSeason = getScalarValue(query, 'season');
  if (rawYear === undefined && rawSeason === undefined) {
    return {
      status: 'selection-required',
      value: { ...pagination.value, minTotal: minTotal.value },
    };
  }
  if (rawYear === undefined || rawSeason === undefined) {
    return { status: 'invalid', reason: 'incomplete-season-selection' };
  }

  const year = parseInteger(rawYear, 1000, 9999);
  if (year === undefined) {
    return { status: 'invalid', reason: 'invalid-year' };
  }

  const seasons: readonly SeasonName[] = ['winter', 'spring', 'summer', 'fall'];
  if (!seasons.includes(rawSeason as SeasonName)) {
    return { status: 'invalid', reason: 'invalid-season' };
  }

  return {
    status: 'valid',
    value: { year, season: rawSeason as SeasonName, minTotal: minTotal.value, ...pagination.value },
  };
}

export function parseSearchRoute(query: RawRouteValues): ParsedRoute<SearchRequest> {
  if (hasInvalidScalarValue(query, 'q')) {
    return { status: 'invalid', reason: 'invalid-query' };
  }

  const rawQuery = getScalarValue(query, 'q');
  const normalizedQuery = rawQuery?.trim();
  if (normalizedQuery === undefined || normalizedQuery.length === 0) {
    return { status: 'invalid', reason: 'invalid-query' };
  }

  const pagination = parsePagination(query);
  return pagination.status === 'invalid'
    ? pagination
    : { status: 'valid', value: { query: normalizedQuery, ...pagination.value } };
}

export type RankingRequest =
  | { readonly type: 'top_score'; readonly request: TopScoreRankingRequest }
  | { readonly type: 'most_rated'; readonly request: MostRatedRankingRequest };

export function parseRankingRoute(
  query: RawRouteValues,
  rankingType: RankingType,
): ParsedRoute<RankingRequest> {
  const pagination = parsePagination(query);
  if (pagination.status === 'invalid') {
    return pagination;
  }

  if (rankingType === 'most_rated') {
    if (query.min_total !== undefined) {
      return { status: 'invalid', reason: 'unsupported-ranking-parameter' };
    }
    return { status: 'valid', value: { type: rankingType, request: pagination.value } };
  }

  const minTotal = parseMinTotal(query);
  return minTotal.status === 'invalid'
    ? minTotal
    : {
        status: 'valid',
        value: { type: rankingType, request: { minTotal: minTotal.value, ...pagination.value } },
      };
}

export function parsePositiveBgmId(params: RawRouteValues): ParsedRoute<BgmId> {
  if (hasInvalidScalarValue(params, 'bgmId')) {
    return { status: 'invalid', reason: 'invalid-bgm-id' };
  }

  const rawBgmId = getScalarValue(params, 'bgmId');
  const bgmId =
    rawBgmId === undefined ? undefined : parseInteger(rawBgmId, 1, Number.MAX_SAFE_INTEGER);
  return bgmId === undefined
    ? { status: 'invalid', reason: 'invalid-bgm-id' }
    : { status: 'valid', value: bgmId };
}
