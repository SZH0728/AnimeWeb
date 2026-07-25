export class ApiError extends Error {
  public readonly status: number;
  public readonly code: string;

  public constructor(status: number, code: string, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
  }
}

export class NetworkError extends Error {
  public constructor(cause: unknown) {
    super('网络请求失败。', { cause });
    this.name = 'NetworkError';
  }
}

export class ResponseContractError extends Error {
  public constructor(message: string, cause?: unknown) {
    super(message, { cause });
    this.name = 'ResponseContractError';
  }
}

export function isRequestCancelled(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError';
}
