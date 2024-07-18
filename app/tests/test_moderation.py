import pytest

from ..services.llm_moderation import moderation_service


@pytest.mark.asyncio
async def test_moderate_content_service():
    """
    Test functionality of content moderation service.

    This test ensures, that moderation service, based on OpenAI moderation endpoint, will flag inappropriate content.
    """
    harmless_content = "I love kittens! They're so fluffy and cute UwU"
    harmful_content = "Go jump off the bridge you moron"

    harmless_response = await moderation_service.moderate_content(harmless_content)
    assert not harmless_response["flagged"]

    harmful_response = await moderation_service.moderate_content(harmful_content)
    assert harmful_response["flagged"]
