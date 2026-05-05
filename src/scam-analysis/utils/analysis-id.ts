/**
 * Generates a UUID v4 to uniquely identify a single analysis run.
 * Uses the Web Crypto global available in Node 19+ — no import required.
 */
export function generateAnalysisId(): string {
  return `analysis_${globalThis.crypto.randomUUID()}`;
}
