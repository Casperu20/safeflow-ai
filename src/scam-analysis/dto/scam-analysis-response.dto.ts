import { EvidenceSnippet as EvidenceSnippetDto } from './evidence-snippet.dto';

/**
 * Three-tier risk classification derived from the numeric score.
 *
 *  0 – 39  → low
 * 40 – 69  → medium
 * 70 – 100 → high
 */
export type ScamRiskLevel = 'low' | 'medium' | 'high';

export type ScamAnalysisResponseDto = {
  /** Unique identifier for this analysis run (UUID v4). */
  analysisId: string;

  /**
   * Integer risk score normalised to 0–100.
   * 0 = no scam signal detected; 100 = extremely high confidence of scam.
   */
  riskScore: number;

  /** Human-readable tier derived from riskScore. */
  riskLevel: ScamRiskLevel;

  /**
   * Detected scam category (e.g. "invoice fraud", "phishing").
   * Null when no specific type can be identified.
   */
  detectedScamType?: string;

  /** Detailed explanation of the model's finding. */
  explanation: string;

  /** Ordered list of high-level scam signal labels identified in the text. */
  indicators: string[];

  /**
   * Verbatim evidence fragments from the submitted text.
   * Optional — absent when no clear evidence was found.
   */
  evidence?: EvidenceSnippetDto[];

  /** Recommended action for the end user or downstream system. */
  recommendation: string;
};
