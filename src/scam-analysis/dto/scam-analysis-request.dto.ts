import { IsNotEmpty, IsString, MaxLength } from 'class-validator';

export class ScamAnalysisRequestDto {
  /**
   * MVP supports plain text payloads only.
   * PDF/image extraction will be added in a later iteration.
   */
  @IsString()
  inputType!: string;

  /**
   * Pre-extracted plain text content to analyse.
   * The value is treated as untrusted data and never executed.
   */
  @IsString()
  @IsNotEmpty()
  @MaxLength(20_000)
  content!: string;
}
