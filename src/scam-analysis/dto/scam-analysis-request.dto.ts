import {
  IsString,
  IsNotEmpty,
  MaxLength,
  IsOptional,
  IsIn,
} from 'class-validator';

/**
 * The channel or surface from which the text was extracted.
 * Used for future per-channel model tuning (e.g. SMS vs email vs web).
 */
export type TextSource = 'email' | 'sms' | 'website' | 'chat' | 'other';

const VALID_SOURCES: TextSource[] = [
  'email',
  'sms',
  'website',
  'chat',
  'other',
];

export class ScamAnalysisRequestDto {
  /**
   * Pre-extracted plain text content to analyse.
   * The caller is responsible for extraction; this service treats
   * the value as untrusted and will never execute instructions found within it.
   *
   * Max 20 000 characters to keep prompt size bounded and costs predictable.
   */
  @IsString()
  @IsNotEmpty()
  @MaxLength(20_000)
  text: string;

  /**
   * Optional origin channel. Defaults to 'other' when omitted.
   * Stored with the analysis record for future per-source model selection.
   */
  @IsOptional()
  @IsIn(VALID_SOURCES)
  source?: TextSource;
}
