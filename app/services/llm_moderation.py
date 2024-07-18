import httpx
from ..core.config import settings


class ModerationService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/moderations"

    async def moderate_content(self, content: str) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "input": content,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, json=data, headers=headers)
            response.raise_for_status()
            return response.json().get("results")[0]


moderation_service = ModerationService(api_key=settings.OPENAI_API_KEY)
