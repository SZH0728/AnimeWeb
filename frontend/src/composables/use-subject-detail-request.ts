import type { SubjectDetail } from '@/api/api-contract';
import { fetchSubjectDetail } from '@/api/subjects-api';
import { useRequestState, type RequestState } from '@/composables/use-request-state';
import type { BgmId } from '@/types/api-requests';

export type SubjectDetailRequestState = RequestState<SubjectDetail, BgmId>;

export function useSubjectDetailRequest(): SubjectDetailRequestState {
  return useRequestState(fetchSubjectDetail);
}
