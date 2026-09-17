from langchain_core.tools import tool
from langgraph.runtime import get_runtime

from erp_agent_graph.context import Context
from erp_agent_graph.models.customer import Customer


@tool
def find_customer_by_email(email: str) -> Customer | None:
    """Find the registered customer with exactly this email address.

    Try this one first: when it finds something, the identification is certain.
    """
    repo = get_runtime(Context).context.customer_repository
    return repo.find_by_email(email)


@tool
def find_customer_by_domain(email: str) -> Customer | None:
    """Find the customer from the domain of the email address.

    Use it when find_customer_by_email finds nothing: in business, a new address
    on an already known domain is almost always the same company. Returns None
    when the domain is unknown or matches more than one customer.
    """
    repo = get_runtime(Context).context.customer_repository
    return repo.find_by_domain(email)


@tool
def search_customers_by_name(name: str) -> list[Customer]:
    """Search customers by company name, partial matches included, case-insensitive.

    Use it when neither the address nor the domain returns anything, with the
    company name read from the signature, the subject or the body of the email.
    If nothing comes back, try again with a shorter part of the name:
    "Rossi Impianti Srl" -> "Rossi Impianti" -> "Rossi".

    It may return several candidates: pick one only if the rest of the email
    confirms it, otherwise leave the decision to a person.
    """
    repo = get_runtime(Context).context.customer_repository
    return repo.search_by_name(name)
