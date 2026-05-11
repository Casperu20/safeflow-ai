import asyncio
import sys
sys.path.insert(0, 'backend')
from app.services.ai_service_client import AiServiceClient

async def test():
    client = AiServiceClient()
    try:
        result = await client.analyze_text('Urgent verify now new bank details')
        print("Success!")
        print(result)
    except Exception as e:
        print(f"Error: {type(e).__name__}")
        print(f"Message: {str(e)}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
