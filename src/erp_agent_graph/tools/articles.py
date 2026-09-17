from langchain_core.tools import tool
from langgraph.runtime import get_runtime

from erp_agent_graph.context import Context
from erp_agent_graph.models.article import Article
from erp_agent_graph.services.article_repository import ArticleRepository


@tool
def find_article_by_code(code: str) -> Article | None:
    """Check whether an article code exists in the catalogue, and return it.

    Use it when the email states a code explicitly, to make sure it is one of ours
    before putting it in an order line. Returns None when the code does not exist:
    in that case do not use that code, search the catalogue with
    search_articles_by_description using the words the customer wrote.
    """
    repo: ArticleRepository = get_runtime(Context).context.article_repository

    article = repo.find_by_code(code)

    return article


@tool
def find_articles_by_codes(codes: list[str]) -> list[Article]:
    """Check which of these article codes exist in the catalogue, and return them.

    Use it when the email states several codes at once, to check them in one go.
    Codes that do not exist are simply missing from the result.
    """

    repo: ArticleRepository = get_runtime(Context).context.article_repository

    articles: list[Article] = repo.find_many_by_codes(codes)
    return articles


@tool
def search_by_description(name: str) -> list[Article]:
    """
    search articles by their description provided in the mail.
    It could be a partial match, investigate whether the article exists,
    and find the best matching article in the catalogue.
    """

    repo: ArticleRepository = get_runtime(Context).context.article_repository

    articles: list[Article] = repo.search_by_description(name)

    return articles
