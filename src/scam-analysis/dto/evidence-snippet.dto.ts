import { ScamRiskLevel } from './scam-analysis-response.dto';

export type EvidenceSnippet = {
  /** Verbatim fragment from the submitted text that triggered this flag. */
  text: string;

  /** Human-readable explanation of why this fragment is suspicious. */
  reason: string;

  /** Severity tier of this individual piece of evidence. */
  severity: ScamRiskLevel;
};
