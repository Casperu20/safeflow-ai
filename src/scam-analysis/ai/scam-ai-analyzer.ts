import OpenAI from 'openai';
import { ScamAiResponseSchema, ScamAiResponse } from './scam-ai.schema';
import {
  SCAM_ANALYSIS_SYSTEM_PROMPT,
  buildScamAnalysisUserPrompt,
} from './scam-ai.prompt';
import { normaliseScore, mapScoreToRiskLevel } from './scam-risk.mapper';

export class ScamAiAnalyzer {
  constructor(private readonly openai: OpenAI) {}

  async analyzeText(inputText: string): Promise<ScamAiResponse> {
    let rawContent: string;

    try {
      const completion = await this.openai.chat.completions.create({
        model: 'gpt-4.1-mini',
        response_format: { type: 'json_object' },
        messages: [
          { role: 'system', content: SCAM_ANALYSIS_SYSTEM_PROMPT },
          { role: 'user', content: buildScamAnalysisUserPrompt(inputText) },
        ],
      });

      rawContent = completion.choices[0]?.message?.content ?? '';
    } catch (err) {
      throw new ScamAiAnalysisError(
        'OpenAI request failed',
        err instanceof Error ? err : undefined,
      );
    }

    let parsed: unknown;
    try {
      parsed = JSON.parse(rawContent);
    } catch {
      throw new ScamAiAnalysisError(
        'OpenAI returned invalid JSON — treating as analysis failure',
      );
    }

    const result = ScamAiResponseSchema.safeParse(parsed);
    if (!result.success) {
      throw new ScamAiAnalysisError(
        `OpenAI response failed schema validation: ${result.error.message}`,
      );
    }

    // Normalise score to [0, 100] integer and recompute riskLevel independently
    // of what the model returned — never trust the model's own riskLevel field.
    const normalisedScore = normaliseScore(result.data.riskScore);
    const recomputedRiskLevel = mapScoreToRiskLevel(normalisedScore);

    return {
      ...result.data,
      riskScore: normalisedScore,
      riskLevel: recomputedRiskLevel,
    };
  }
}

export class ScamAiAnalysisError extends Error {
  constructor(message: string, public readonly cause?: Error) {
    super(message);
    this.name = 'ScamAiAnalysisError';
  }
}
