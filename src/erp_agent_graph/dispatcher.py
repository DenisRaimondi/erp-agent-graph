import logging
import os
import time

import httpx
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import Connection
from psycopg.rows import DictRow, dict_row
from psycopg_pool import ConnectionPool

from erp_agent_graph.context import Context
from erp_agent_graph.graph import builder
from erp_agent_graph.llm import SoftToolChoiceDeepSeek
from erp_agent_graph.models.inbound_mail import InboundMail, MailStatus
from erp_agent_graph.services.article_repository import ArticleRepository
from erp_agent_graph.services.customer_repository import CustomerRepository
from erp_agent_graph.services.mail_repository import MailRepository
from erp_agent_graph.services.mailpit import MailpitService
from erp_agent_graph.services.order_repository import OrderRepository
from erp_agent_graph.state import PartialState

load_dotenv()
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("MAILPIT_URL") or "http://localhost:8025"
DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql://erp:erp@localhost:5433/erp"


def mark_all_unread(http_client: httpx.Client) -> None:
    """DEVELOPMENT ONLY: marks every message in the mailbox as unread again.

    Reading a body with /api/v1/message/{id} marks the email as read: without this,
    after the first pass the mailbox looks empty and a run cannot be repeated.
    To be removed once the graph runs on its own.
    """
    messages = http_client.get("/api/v1/messages", params={"limit": 200}).json()["messages"]
    ids = [m["ID"] for m in messages]

    if ids:
        # Mailpit answers "ok" as plain text, not JSON: do not call .json() on it.
        http_client.put("/api/v1/messages", json={"IDs": ids, "Read": False})
        logger.info("marked %d emails as unread again", len(ids))


def main():

    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
    # httpx and httpcore log every request and every connection detail: at DEBUG
    # that is dozens of lines for each turn of the loop.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # Thinking mode refuses `temperature`, and refuses the forced tool_choice that
    # LangChain sets for structured output: see SoftToolChoiceDeepSeek.
    llm_model = SoftToolChoiceDeepSeek(
        model="deepseek-flash",
        extra_body={"thinking": {"type": "enabled"}},
        reasoning_effort="medium",
    )

    with (
        httpx.Client(base_url=BASE_URL) as http_client,
        ConnectionPool(
            DATABASE_URL,
            connection_class=Connection[DictRow],
            kwargs={"autocommit": True, "row_factory": dict_row},
        ) as checkpointer_pool,
    ):
        context = Context(
            llm_model=llm_model,
            customer_repository=CustomerRepository(checkpointer_pool),
            article_repository=ArticleRepository(checkpointer_pool),
            order_repository=OrderRepository(checkpointer_pool),
        )
        mailpit_service = MailpitService(http_client)
        mail_repository = MailRepository(checkpointer_pool)

        saver = PostgresSaver(checkpointer_pool)

        saver.setup()

        graph = builder.compile(saver)

        while True:
            # mark_all_unread(http_client)

            emails = mailpit_service.get_unread_emails()

            for email in emails:
                body = mailpit_service.get_body(email.id)

                email.body = body

                # Claiming the email is also the guard against picking up a run that
                # is already going, or one suspended on an interrupt waiting for a
                # person: the register answers None and we move on.
                claimed = mail_repository.claim(
                    InboundMail(
                        thread_id=email.id,
                        status="processing",
                        sender=email.sender,
                        subject=email.subject,
                        body=email.body,
                        received_at=email.created_at,
                    )
                )

                if claimed is None:
                    logger.info("email %s already in the register, skipped", email.id)
                    continue

                config: RunnableConfig = {"configurable": {"thread_id": email.id}}

                # Only the run is guarded: a write that fails here must not be read as
                # a run that failed.
                try:
                    result = graph.invoke(
                        PartialState(email=email), context=context, config=config, version="v2"
                    )
                except Exception:
                    logger.exception("email %s failed", email.id)
                    mail_repository.update_status(email.id, "failed")
                    continue

                # The order path always stops on confirm_customer, so anything that ran to the
                # end was thrown away by the classifier.
                status: MailStatus = "interrupted" if result.interrupts else "discarded"
                mail_repository.update_status(email.id, status)

            time.sleep(60)


if __name__ == "__main__":
    main()
