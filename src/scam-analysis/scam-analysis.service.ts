import { ScamAiAnalyzer, ScamAiAnalysisError } from './ai/scam-ai-analyzer';
import { ScamAnalysisResponseDto } from './dto/scam-analysis-response.dto';
import { generateAnalysisId } from './utils/analysis-id';
import {
  ScamAnalysisError,
  ScamAnalysisErrorCode,
} from './errors/scam-analysis.errors';

export class ScamAnalysisService {
  constructor(private readonly scamAiAnalyzer: ScamAiAnalyzer) {}

  async analyzeText(content: string): Promise<ScamAnalysisResponseDto> {
    if (!content || content.trim().length === 0) {
      throw new ScamAnalysisError(
        ScamAnalysisErrorCode.EMPTY_TEXT_CONTENT,
        'Submitted text content must not be empty.',
        400,
      );
    }

    const analysisId = generateAnalysisId();

    let aiResponse;
    try {
      aiResponse = await this.scamAiAnalyzer.analyzeText(content);
    } catch (err) {
      if (err instanceof ScamAiAnalysisError) {
        throw new ScamAnalysisError(
          ScamAnalysisErrorCode.ANALYSIS_FAILED,
          'Scam analysis could not be completed. Please try again.',
          502,
        );
      }
      throw new ScamAnalysisError(
        ScamAnalysisErrorCode.SERVER_ERROR,
        'An unexpected error occurred during analysis.',
        500,
      );
    }

    const response: ScamAnalysisResponseDto = {
      analysisId,
      riskScore: aiResponse.riskScore,
      riskLevel: aiResponse.riskLevel,
      explanation: aiResponse.explanation,
      indicators: aiResponse.indicators,
      recommendation: aiResponse.recommendation,
      ...(aiResponse.detectedScamType != null && {
        detectedScamType: aiResponse.detectedScamType,
      }),
      ...(aiResponse.evidence && aiResponse.evidence.length > 0 && {
        evidence: aiResponse.evidence,
      }),
    };

    return response;
  }
}
