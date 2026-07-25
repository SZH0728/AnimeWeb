import { onScopeDispose, readonly, ref, type DeepReadonly, type Ref } from 'vue';

import { isRequestCancelled } from '@/api/api-error';

export interface RequestState<T, TInput> {
  readonly data: DeepReadonly<Ref<T | null>>;
  readonly loading: DeepReadonly<Ref<boolean>>;
  readonly error: DeepReadonly<Ref<Error | null>>;
  load(input: TInput): Promise<void>;
  retry(): Promise<void>;
  cancel(): void;
}

export function useRequestState<T, TInput>(
  request: (input: TInput, signal: AbortSignal) => Promise<T>,
): RequestState<T, TInput> {
  const data = ref<T | null>(null);
  const loading = ref(false);
  const error = ref<Error | null>(null);
  let activeController: AbortController | null = null;
  let requestId = 0;
  let latestInput: TInput | null = null;

  async function load(input: TInput): Promise<void> {
    activeController?.abort();
    const controller = new AbortController();
    activeController = controller;
    latestInput = input;
    const currentRequestId = ++requestId;

    loading.value = true;
    error.value = null;

    try {
      const response = await request(input, controller.signal);
      if (currentRequestId === requestId) {
        data.value = response;
      }
    } catch (caught: unknown) {
      if (currentRequestId === requestId && !isRequestCancelled(caught)) {
        error.value = caught instanceof Error ? caught : new Error('请求失败。', { cause: caught });
      }
    } finally {
      if (currentRequestId === requestId) {
        loading.value = false;
        activeController = null;
      }
    }
  }

  async function retry(): Promise<void> {
    if (latestInput !== null) {
      await load(latestInput);
    }
  }

  function cancel(): void {
    activeController?.abort();
    activeController = null;
    requestId += 1;
    loading.value = false;
  }

  onScopeDispose((): void => {
    cancel();
  });

  return {
    data: readonly(data),
    loading: readonly(loading),
    error: readonly(error),
    load,
    retry,
    cancel,
  };
}
