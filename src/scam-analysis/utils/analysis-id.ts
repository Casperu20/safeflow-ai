import { randomUUID } from 'crypto';

/**
 * Generates a UUID v4 to uniquely identify a single analysis run.
 * Uses Node's built-in crypto module — no external dependency required.
 */
export function generateAnalysisId(): string {
  return `analysis_${randomUUID()}`;
}
