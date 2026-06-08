import json
from openai import AsyncOpenAI
from app.config import settings
from app.schemas.lead import ClassificationInput, ClassificationOutput

class AIClassifierService:
    def __init__(self):
        # Fallback to mock if API key is default/empty
        self.use_mock = settings.OPENAI_API_KEY == "mock-key" or not settings.OPENAI_API_KEY
        if not self.use_mock:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def classify_intent(self, data: ClassificationInput) -> ClassificationOutput:
        if self.use_mock:
            return self._mock_classification(data.message)

        try:
            # System prompt with strict JSON mode execution
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AI data router. Classify incoming customer messages into "
                            "one of these intents: [sales_enquiry, support, partnership, spam]. "
                            "Output a JSON object containing keys 'intent' (string) and 'confidence' (float between 0.0 and 1.0)."
                        )
                    },
                    {"role": "user", "content": f"Message: {data.message}"}
                ],
                temperature=0.0  # High determinism
            )

            result = json.loads(response.choices[0].message.content)
            return ClassificationOutput(
                intent=result.get("intent", "spam"),
                confidence=result.get("confidence", 0.5)
            )
        except Exception:
            # Failure resiliency fallback
            return self._mock_classification(data.message)

    def _mock_classification(self, message: str) -> ClassificationOutput:
        msg = message.lower()
        if any(w in msg for w in ["interest", "buy", "service", "pricing", "cost", "demo"]):
            return ClassificationOutput(intent="sales_enquiry", confidence=0.95)
        if any(w in msg for w in ["help", "issue", "error", "broken", "login"]):
            return ClassificationOutput(intent="support", confidence=0.91)
        return ClassificationOutput(intent="spam", confidence=0.85)
