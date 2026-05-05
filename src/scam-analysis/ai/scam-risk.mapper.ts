import { ScamRiskLevel } from '../dto/scam-analysis-response.dto';

/**
 * Thresholds that define the three risk tiers.
 *
 *  0 – 39  → low
 * 40 – 69  → medium
 * 70 – 100 → high
 *
 * Centralised here so that future work (e.g. per-channel tuning or
 * A/B threshold experiments) only needs to change this one place.
 */
const RISK_THRESHOLDS = {
  LOW_MAX: 39,
  MEDIUM_MAX: 69,
} as const;

/**
 * Maps a raw integer risk score (0–100) to the corresponding ScamRiskLevel.
 *
 * @throws {RangeError} if score is outside the valid [0, 100] range.
 */
export function mapScoreToRiskLevel(score: number): ScamRiskLevel {
  if (score < 0 || score > 100) {
    throw new RangeError(
      `Risk score must be between 0 and 100, received: ${score}`,
    );
  }

  if (score <= RISK_THRESHOLDS.LOW_MAX) return 'low';
  if (score <= RISK_THRESHOLDS.MEDIUM_MAX) return 'medium';
  return 'high';
}

/**
 * Clamps an arbitrary number to the valid [0, 100] integer range.
 * Used as a defensive step before calling mapScoreToRiskLevel when the
 * score source (e.g. a future LightGBM model) may return floats or
 * out-of-range values.
 */
export function normaliseScore(raw: number): number {
  return Math.round(Math.min(100, Math.max(0, raw)));
}
