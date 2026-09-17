from erp_agent_graph.models.customer import Customer
from erp_agent_graph.services.base_repository import BaseRepository

# Matching on these domains makes no sense: anyone can have an address there.
DOMINI_PUBBLICI = frozenset(
    {
        "gmail.com",
        "googlemail.com",
        "outlook.com",
        "hotmail.com",
        "hotmail.it",
        "live.com",
        "yahoo.com",
        "yahoo.it",
        "icloud.com",
        "libero.it",
        "virgilio.it",
        "alice.it",
        "tiscali.it",
        "pec.it",
    }
)


class CustomerRepository(BaseRepository):
    def find_by_email(self, email: str) -> Customer | None:
        return self._get_one(
            Customer,
            "SELECT customers.* FROM customers" + "\n"
            "JOIN customer_emails on customer_emails.customer_id = customers.id" + "\n"
            "WHERE customer_emails.email = %s",
            (email,),
        )

    def find_by_domain(self, email: str) -> Customer | None:
        """The customer matching the email domain, when there is exactly one.

        Riceve l'email intera e ne ricava il dominio: chi chiama non deve pensarci.
        Returns None when more than one customer matches too, because an order
        attributed to the wrong customer is worse than one left unattributed.
        """
        domain = email.rpartition("@")[2].lower()
        if not domain or domain in DOMINI_PUBBLICI:
            return None

        # LIMIT 2, not 1: two rows are enough to know it is ambiguous, without reading all.
        candidati = self._get_all(
            Customer,
            "SELECT DISTINCT customers.* FROM customers\n"
            "JOIN customer_emails ON customer_emails.customer_id = customers.id\n"
            "WHERE split_part(customer_emails.email, '@', 2) = %s\n"
            "LIMIT 2",
            (domain,),
        )

        return candidati[0] if len(candidati) == 1 else None

    def search_by_name(self, name: str) -> list[Customer]:
        return self._get_all(
            Customer, "SELECT * FROM customers where name ILIKE %s", (f"%{name}%",)
        )
