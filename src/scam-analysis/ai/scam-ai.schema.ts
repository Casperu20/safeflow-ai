import { z } from 'zod';

/**
 * Zod schema for the raw JSON object that OpenAI must return.
 *
 * This is the contract between the AI layer and the rest of the pipeline.
 * All fields are required unless marked optional; the mapper will reject
 * responses that don't conform.
 *
 * Intentionally kept separate from the response DTO so the AI contract
 * can evolve independently of what we expose to the frontend.
 */

const ScamRiskLevelSchema = z.enum(['low', 'medium', 'high']);

export const EvidenceSnippetSchema = z.object({
  /**
   * Short verbatim fragment from the submitted text.
   * The model must not fabricate snippets not present in the input.
   */
  text: z.string().min(1).max(500),

  /** Why this fragment is suspicious. */
  reason: z.string().min(1).max(500),

  /** Severity tier for this individual piece of evidence. */
  severity: ScamRiskLevelSchema,
});

export const ScamAiResponseSchema = z.object({
  /**
   * Integer risk score in [0, 100].
   * The model is prompted to reason step-by-step before assigning the score.
   */
  riskScore: z.number().int().min(0).max(100),

  /** Three-tier risk classification. Must be consistent with riskScore. */
  riskLevel: ScamRiskLevelSchema,

  /**
   * Detected scam category (e.g. "invoice fraud", "phishing").
   * Null when no specific type can be identified.
   */
  detectedScamType: z.string().nullable(),

  /**
   * Detailed explanation of the model's finding.
   * Safe to render in a UI after HTML-encoding.
   */
  explanation: z.string().min(1).max(1000),

  /**
   * High-level scam signal labels (e.g. "urgency pressure", "impersonation").
   * Empty array when no signals were detected.
   */
  indicators: z.array(z.string()).max(20),

  /**
   * Up to 5 verbatim evidence snippets from the submitted text.
   * Empty array is valid when riskScore < 40 and no clear indicators exist.
   */
  evidence: z.array(EvidenceSnippetSchema).max(5),

  /** Recommended action for the end user or downstream system. */
  recommendation: z.string().min(1).max(500),
});

/** Inferred TypeScript type of a validated AI response. */
export type ScamAiResponse = z.infer<typeof ScamAiResponseSchema>;
export type EvidenceSnippetAi = z.infer<typeof EvidenceSnippetSchema>;
