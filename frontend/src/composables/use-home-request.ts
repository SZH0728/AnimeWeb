import type { HomeResponse } from '@/api/api-contract';
import { fetchHome } from '@/api/home-api';
import { useRequestState, type RequestState } from '@/composables/use-request-state';

export type HomeRequestState = RequestState<HomeResponse, undefined>;

export function useHomeRequest(): HomeRequestState {
  return useRequestState<HomeResponse, undefined>(
    (_input: undefined, signal: AbortSignal): Promise<HomeResponse> => fetchHome(signal),
  );
}
