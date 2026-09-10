from langchain_core.tools import tool
from langgraph.runtime import get_runtime

from erp_agent_graph.context import Context
from erp_agent_graph.models.customer import Customer


@tool
def find_customer_by_email(email: str) -> Customer | None:
    """Cerca il cliente censito con esattamente questo indirizzo email.

    Provalo per primo: se trova qualcosa, l'identificazione e' certa.
    """
    repo = get_runtime(Context).context.customer_repository
    return repo.find_by_email(email)


@tool
def find_customer_by_domain(email: str) -> Customer | None:
    """Cerca il cliente a partire dal dominio dell'indirizzo email.

    Usalo quando find_customer_by_email non trova nulla: in ambito aziendale un
    indirizzo nuovo su un dominio gia' noto e' quasi sempre la stessa azienda.
    Restituisce None se il dominio non e' censito o se corrisponde a piu' clienti.
    """
    repo = get_runtime(Context).context.customer_repository
    return repo.find_by_domain(email)


@tool
def search_customers_by_name(name: str) -> list[Customer]:
    """Cerca clienti per ragione sociale, anche parziale, ignorando maiuscole.

    Usalo quando ne' l'indirizzo ne' il dominio danno un risultato, provando con
    il nome dell'azienda letto dalla firma, dall'oggetto o dal corpo della mail.
    Se non trovi nulla, riprova con una parte piu' corta del nome:
    "Rossi Impianti Srl" -> "Rossi Impianti" -> "Rossi".

    Puo' restituire piu' candidati: scegline uno solo se il resto della mail lo
    conferma, altrimenti lascia decidere a una persona.
    """
    repo = get_runtime(Context).context.customer_repository
    return repo.search_by_name(name)
