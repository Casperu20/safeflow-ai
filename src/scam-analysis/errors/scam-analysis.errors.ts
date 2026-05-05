export enum ScamAnalysisErrorCode {
  INVALID_INPUT_TYPE = 'INVALID_INPUT_TYPE',
  FILE_TOO_LARGE = 'FILE_TOO_LARGE',
  UNSUPPORTED_FILE_TYPE = 'UNSUPPORTED_FILE_TYPE',
  PDF_TEXT_EXTRACTION_FAILED = 'PDF_TEXT_EXTRACTION_FAILED',
  OCR_FAILED = 'OCR_FAILED',
  EMPTY_TEXT_CONTENT = 'EMPTY_TEXT_CONTENT',
  CONTENT_TOO_LONG = 'CONTENT_TOO_LONG',
  ANALYSIS_FAILED = 'ANALYSIS_FAILED',
  MODEL_UNAVAILABLE = 'MODEL_UNAVAILABLE',
  RATE_LIMITED = 'RATE_LIMITED',
  SERVER_ERROR = 'SERVER_ERROR',
}

export type ApiErrorDto = {
  errorCode: ScamAnalysisErrorCode;
  message: string;
  details?: Record<string, string[]>;
};

export class ScamAnalysisError extends Error {
  constructor(
    public readonly errorCode: ScamAnalysisErrorCode,
    message: string,
    public readonly statusCode: number,
    public readonly details?: Record<string, string[]>,
  ) {
    super(message);
    this.name = 'ScamAnalysisError';
  }

  toApiErrorDto(): ApiErrorDto {
    return {
      errorCode: this.errorCode,
      message: this.message,
      ...(this.details !== undefined && { details: this.details }),
    };
  }
}
