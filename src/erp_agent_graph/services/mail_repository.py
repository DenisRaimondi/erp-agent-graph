from erp_agent_graph.models.inbound_mail import InboundMail, MailStatus
from erp_agent_graph.services.base_repository import BaseRepository


class MailRepository(BaseRepository):
    def claim(self, mail: InboundMail) -> InboundMail | None:
        """Record that this email has been picked up.

        Returns None when the email was already in the register: the insert and
        the check are one statement, so two dispatchers racing on the same email
        cannot both win.
        """
        return self._write_one(
            InboundMail,
            """
            INSERT INTO inbound_mails (thread_id, status, sender, subject, body, received_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (thread_id) DO NOTHING
            RETURNING *
            """,
            (
                mail.thread_id,
                mail.status,
                mail.sender,
                mail.subject,
                mail.body,
                mail.received_at,
            ),
        )

    def update_status(self, thread_id: str, status: MailStatus) -> InboundMail | None:
        """Move the email to `status`. Returns None when it was never claimed."""
        return self._write_one(
            InboundMail,
            """
            UPDATE inbound_mails
            SET status = %s,
                updated_at = now()
            WHERE thread_id = %s
            RETURNING *
            """,
            (status, thread_id),
        )

    def list_by_status(self, status: MailStatus) -> list[InboundMail]:
        """The register, newest first, for one status: the web app's queue."""
        return self._get_all(
            InboundMail,
            """
            SELECT *
            FROM inbound_mails
            WHERE status = %s
            ORDER BY received_at DESC
            """,
            (status,),
        )
