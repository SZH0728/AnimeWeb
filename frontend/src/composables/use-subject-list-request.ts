import type { SubjectListResponse } from '@/api/api-contract';
import { fetchSubjects } from '@/api/subjects-api';
import { useRequestState, type RequestState } from '@/composables/use-request-state';
import type { SubjectListRequest } from '@/types/api-requests';

export type SubjectListRequestState = RequestState<SubjectListResponse, SubjectListRequest>;

export function useSubjectListRequest(): SubjectListRequestState {
  return useRequestState(fetchSubjects);
}
