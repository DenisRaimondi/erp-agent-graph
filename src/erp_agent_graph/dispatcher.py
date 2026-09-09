import logging
import os
import time

import httpx
from dotenv import load_dotenv

from erp_agent_graph.services.mailpit import MailpitService

load_dotenv()
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("MAILPIT_URL") or "http://localhost:8025"


def rimetti_tutte_non_lette(http_client: httpx.Client) -> None:
    """SOLO SVILUPPO: riporta a "non letta" ogni mail nella casella.

    Serve perché leggere il corpo con /api/v1/message/{id} marca la mail come letta:
    senza questo, dopo il primo giro la casella risulta vuota e non si può riprovare.
    Da togliere quando il grafo sarà collegato.
    """
    messages = http_client.get("/api/v1/messages", params={"limit": 200}).json()["messages"]
    ids = [m["ID"] for m in messages]

    if ids:
        # Mailpit risponde "ok" in testo semplice, non JSON: non chiamarci .json().
        http_client.put("/api/v1/messages", json={"IDs": ids, "Read": False})
        logger.info("rimesse non lette %d mail", len(ids))


def main():

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

    with httpx.Client(base_url=BASE_URL) as http_client:
        mailpit_service = MailpitService(http_client)

        while True:
            rimetti_tutte_non_lette(http_client)

            emails = mailpit_service.get_unread_emails()

            for email in emails:
                body = mailpit_service.get_body(email.id)
                email.body = body

            time.sleep(60)


if __name__ == "__main__":
    main()
