import { Module } from '@nestjs/common';
import OpenAI from 'openai';
import { ScamAnalysisController } from './scam-analysis.controller';
import { ScamAnalysisService } from './scam-analysis.service';
import { ScamAiAnalyzer } from './ai/scam-ai-analyzer';

@Module({
  controllers: [ScamAnalysisController],
  providers: [
    ScamAnalysisService,
    ScamAiAnalyzer,
    {
      provide: OpenAI,
      useFactory: () => {
        const apiKey = process.env.OPENAI_API_KEY;
        if (!apiKey) {
          throw new Error(
            'Missing OPENAI_API_KEY environment variable. SafeFlow AI cannot start without an OpenAI API key.',
          );
        }

        return new OpenAI({ apiKey });
      },
    },
  ],
  exports: [ScamAnalysisService],
})
export class ScamAnalysisModule {}
