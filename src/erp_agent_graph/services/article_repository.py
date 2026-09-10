from erp_agent_graph.models.article import Article
from erp_agent_graph.services.base_repository import BaseRepository


class ArticleRepository(BaseRepository):
    def find_by_code(self, code: str) -> Article | None:
        return self._get_one(Article, "SELECT * FROM articles WHERE code = %s", (code,))

    def find_many_by_codes(self, codes: list[str]) -> list[Article]:
        return self._get_all(Article, "SELECT * FROM articles WHERE code = ANY(%s)", (codes,))

    def search_by_description(self, text: str, limit: int = 20) -> list[Article]:
        return self._get_all(
            Article,
            "SELECT * FROM articles WHERE description ILIKE %s LIMIT %s",
            (f"%{text}%", limit),
        )
