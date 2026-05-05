import { Module } from '@nestjs/common';
import { ScamAnalysisModule } from './scam-analysis/scam-analysis.module';

@Module({
  imports: [ScamAnalysisModule],
})
export class AppModule {}
