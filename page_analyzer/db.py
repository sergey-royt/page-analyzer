"""Functions for database access and handling database data"""

import psycopg2
from psycopg2 import pool
from datetime import date
from typing import Callable, Any

from page_analyzer.settings import DATABASE_URL, MINCONN, MAXCONN
from page_analyzer.models import Url, Check


Pool = pool.SimpleConnectionPool(
    minconn=MINCONN, maxconn=MAXCONN, dsn=DATABASE_URL
)


def make_db_connection(query_func: Callable) -> Any | None:
    """Get connection from pull if it's not passed explicitly and
    give it to wrapped query function.
    Make commit amd return connection to the pull after that.
    Make rollback if DatabaseError caused by query function raised."""

    def wrapper(*, conn=None, **kwargs):
        if not conn:
            conn = Pool.getconn()
        try:
            result = query_func(conn=conn, **kwargs)
            conn.commit()
            return result
        except psycopg2.DatabaseError:
            conn.rollback()
        finally:
            Pool.putconn(conn)

    return wrapper


@make_db_connection
def get_url_id(*, conn: Any, url_name: str) -> int | None:
    """
    Retrieve id of web-site from database
    if it had been already added.
    :param conn: Database connection
    :param url_name: normalized url string
    :return: retrieved id or None if nothing was found.
    """

    query = """
    SELECT id
    FROM urls
    WHERE name = %s;"""

    with conn.cursor() as cursor:
        cursor.execute(query, (url_name,))
        url_id_row = cursor.fetchone()

    if url_id_row:
        return url_id_row[0]


@make_db_connection
def get_url_checks(*, conn: Any, url_id: int) -> list[Check | None]:
    """
    :param conn: Database connection
    :param url_id: url_id int
    :return: list with all checks as Check objects
    in case there's no checks return empty list
    """
    query = """
        SELECT id,
        status_code,
        COALESCE(h1, ''),
        COALESCE(title, ''),
        COALESCE(description, ''),
        created_at
        FROM url_checks
        WHERE url_id = %s"""

    with conn.cursor() as cursor:
        cursor.execute(query, (url_id,))
        raw_checks = cursor.fetchall()

    return [
        Check(
            id=id,
            status_code=status_code,
            h1=h1,
            title=title,
            description=description,
            created_at=created_at,
        )
        for id, status_code, h1, title, description, created_at in raw_checks
    ]


@make_db_connection
def get_url(*, conn: Any, url_id: int) -> Url | None:
    """
    By given id
    Return url as Url object if exists
    :param conn: Database connection
    :param url_id: url id int
    """
    query = """
            SELECT *
            FROM urls
            WHERE id = %s
            """

    with conn.cursor() as cursor:
        cursor.execute(query, (url_id,))
        url_row = cursor.fetchone()

    if url_row:
        url_id, name, created_at = url_row
        return Url(id=url_id, name=name, created_at=created_at)


@make_db_connection
def get_all_urls_with_last_check(
        *, conn: Any
) -> list[tuple[Url, Check] | None]:
    """
    :param conn: Database connection
    :return: list of all urls from database
    with last checks result and date if presented
    as tuple containing Url and Check object
    or empty list if there is no urls in database.
    """

    query = """
        SELECT DISTINCT ON (urls.id)
        urls.id,
        urls.name,
        MAX(url_checks.created_at) AS last_check,
        url_checks.status_code
        FROM urls
        LEFT JOIN url_checks ON urls.id = url_checks.url_id
        GROUP BY urls.id, urls.name, url_checks.status_code
        ORDER BY urls.id
        DESC"""

    with conn.cursor() as cursor:
        cursor.execute(query)
        raw_urls = cursor.fetchall()

    return [
        (Url(id, name), Check(created_at=last_check, status_code=status_code))
        for id, name, last_check, status_code in raw_urls
    ]


@make_db_connection
def add_url(*, conn: Any, url_name: str) -> int:
    """Add url to database. Return Id"""

    created_at = date.today()

    query = """INSERT INTO urls
        (name, created_at)
        VALUES (%s, %s)
        RETURNING id"""

    with conn.cursor() as cursor:
        cursor.execute(query, (url_name, created_at))
        url_id = cursor.fetchone()[0]

    return url_id


@make_db_connection
def add_check(*, conn: Any, check: Check) -> None:
    """Add check details to database"""
    created_at = date.today()

    query = """
        INSERT INTO url_checks
        (url_id, status_code, h1, title, description, created_at)
        VALUES (%(url_id)s,
        %(status_code)s,
        %(h1)s,
        %(title)s,
        %(description)s,
        %(created_at)s)"""

    with conn.cursor() as cursor:
        cursor.execute(
            query,
            {
                "url_id": check.url_id,
                "status_code": check.status_code,
                "h1": check.h1,
                "title": check.title,
                "description": check.description,
                "created_at": created_at,
            },
        )
