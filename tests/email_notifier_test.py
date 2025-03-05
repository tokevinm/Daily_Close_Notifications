import pytest
from unittest.mock import AsyncMock, patch
from email_notifier import EmailNotifier


@pytest.mark.asyncio
async def test_get_emails_data():
    notifier = EmailNotifier()
    mock_response = {"users": [{"email": "test@example.com"}]}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.raise_for_status = AsyncMock()
        await notifier.get_emails_data()

    assert notifier.users_data.data[0]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_send_emails():
    notifier = EmailNotifier()
    with patch("aiosmtplib.SMTP", new_callable=AsyncMock) as mock_smtp:
        smtp_instance = mock_smtp.return_value.__aenter__.return_value
        smtp_instance.send_message = AsyncMock(return_value={"result": "success"})

        await notifier.send_emails(
            user_email="test@example.com",
            subject="Test",
            html_text="<p>Hello</p>"
        )

        smtp_instance.send_message.assert_called_once()
