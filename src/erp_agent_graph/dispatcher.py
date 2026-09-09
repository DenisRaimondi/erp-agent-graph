import logging
import os
import time

import httpx
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import Connection
from psycopg.rows import DictRow, dict_row
from psycopg_pool import ConnectionPool

from erp_agent_graph.context import Context
from erp_agent_graph.graph import builder
from erp_agent_graph.services.mailpit import MailpitService
from erp_agent_graph.state import PartialState

load_dotenv()
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("MAILPIT_URL") or "http://localhost:8025"
DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql://erp:erp@localhost:5433/erp"


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

    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
    # httpx e httpcore loggano ogni richiesta e ogni dettaglio della connessione:
    # a DEBUG diventano decine di righe per ogni giro del ciclo.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    llm_model = ChatDeepSeek(
        model="deepseek-v4-pro",
        temperature=0,
        extra_body={"thinking": {"type": "disabled"}},
    )

    context = Context(llm_model=llm_model)

    with (
        httpx.Client(base_url=BASE_URL) as http_client,
        ConnectionPool(
            DATABASE_URL,
            connection_class=Connection[DictRow],
            kwargs={"autocommit": True, "row_factory": dict_row},
        ) as checkpointer_pool,
    ):
        mailpit_service = MailpitService(http_client)

        saver = PostgresSaver(checkpointer_pool)

        saver.setup()

        graph = builder.compile(saver)

        while True:
            rimetti_tutte_non_lette(http_client)

            emails = mailpit_service.get_unread_emails()

            for email in emails:
                body = mailpit_service.get_body(email.id)

                email.body = body

                graph.invoke(
                    PartialState(email=email),
                    context=context,
                    config={"configurable": {"thread_id": email.id}},
                )

            time.sleep(60)


if __name__ == "__main__":
    main()
