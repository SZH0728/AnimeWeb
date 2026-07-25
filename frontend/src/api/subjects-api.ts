import {
  RatingHistoryResponseSchema,
  SubjectDetailSchema,
  SubjectListResponseSchema,
  type RatingHistoryResponse,
  type SubjectDetail,
  type SubjectListResponse,
} from '@/api/api-contract';
import { getJson } from '@/api/http-client';
import type { BgmId, SubjectListRequest } from '@/types/api-requests';
import { buildSubjectListQuery } from '@/utils/query-params';

export function fetchSubjects(
  request: SubjectListRequest,
  signal?: AbortSignal,
): Promise<SubjectListResponse> {
  return getJson(`/subjects?${buildSubjectListQuery(request)}`, SubjectListResponseSchema, signal);
}

export function fetchSubjectDetail(bgmId: BgmId, signal?: AbortSignal): Promise<SubjectDetail> {
  return getJson(`/subjects/${encodeURIComponent(String(bgmId))}`, SubjectDetailSchema, signal);
}

export function fetchRatingHistory(
  bgmId: BgmId,
  signal?: AbortSignal,
): Promise<RatingHistoryResponse> {
  return getJson(
    `/subjects/${encodeURIComponent(String(bgmId))}/ratings`,
    RatingHistoryResponseSchema,
    signal,
  );
}
