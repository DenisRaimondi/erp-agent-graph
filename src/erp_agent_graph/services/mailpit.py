import logging

import httpx

from erp_agent_graph.models.email import Email


class MailpitService:
    def __init__(self, http_client: httpx.Client) -> None:
        self._http_client = http_client

    def get_unread_emails(self) -> list[Email]:
        response = self._http_client.get("/api/v1/search?query=is:unread")

        response.raise_for_status()

        logging.info(f"Response from Mailpit: {response.text}")

        messages = response.json()["messages"]

        emails = [Email.model_validate(m) for m in messages]

        return emails

    def get_body(self, email_id: str) -> str:
        response = self._http_client.get(f"/api/v1/message/{email_id}")

        response.raise_for_status()

        httpMessage = response.json()

        body_message = httpMessage.get("Text") or httpMessage.get("HTML") or ""

        return body_message
