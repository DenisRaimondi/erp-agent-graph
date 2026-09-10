from typing import LiteralString

from psycopg import Connection
from psycopg.rows import DictRow, class_row
from psycopg_pool import ConnectionPool
from pydantic import BaseModel


class BaseRepository:
    def __init__(self, pool: ConnectionPool[Connection[DictRow]]) -> None:
        self._pool = pool

    def _get_one[M: BaseModel](self, model: type[M], sql: LiteralString, params: tuple) -> M | None:
        with self._pool.connection() as conn, conn.cursor(row_factory=class_row(model)) as cur:
            return cur.execute(sql, params).fetchone()

    def _get_all[M: BaseModel](self, model: type[M], sql: LiteralString, params: tuple) -> list[M]:
        with self._pool.connection() as conn, conn.cursor(row_factory=class_row(model)) as cur:
            return cur.execute(sql, params).fetchall()
