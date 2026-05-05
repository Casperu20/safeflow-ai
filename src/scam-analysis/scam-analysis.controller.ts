import {
  Body,
  Controller,
  HttpException,
  InternalServerErrorException,
  Post,
} from '@nestjs/common';
import { ScamAnalysisService } from './scam-analysis.service';
import { ScamAnalysisRequestDto } from './dto/scam-analysis-request.dto';
import { ScamAnalysisResponseDto } from './dto/scam-analysis-response.dto';
import {
  ApiErrorDto,
  ScamAnalysisError,
  ScamAnalysisErrorCode,
} from './errors/scam-analysis.errors';

@Controller('api/scam-analysis')
export class ScamAnalysisController {
  constructor(private readonly scamAnalysisService: ScamAnalysisService) {}

  @Post()
  async analyze(
    @Body() body: ScamAnalysisRequestDto,
  ): Promise<ScamAnalysisResponseDto> {
    try {
      if (body.inputType !== 'text') {
        throw new ScamAnalysisError(
          ScamAnalysisErrorCode.INVALID_INPUT_TYPE,
          'Only inputType="text" is supported for the MVP.',
          400,
          {
            inputType: ['Only "text" is supported at this time.'],
          },
        );
      }

      return await this.scamAnalysisService.analyzeText(body.content);
    } catch (err) {
      if (err instanceof ScamAnalysisError) {
        throw new HttpException(err.toApiErrorDto(), err.statusCode);
      }

      const fallbackError: ApiErrorDto = {
        errorCode: ScamAnalysisErrorCode.SERVER_ERROR,
        message: 'An unexpected server error occurred.',
      };
      throw new InternalServerErrorException(fallbackError);
    }
  }
}
