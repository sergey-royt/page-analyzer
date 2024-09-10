import psycopg2
from psycopg2 import pool
from datetime import date
from typing import Callable, Any

from page_analyzer.settings import DATABASE_URL, MINCONN, MAXCONN
from page_analyzer.models import Url, Check
from page_analyzer.types import Id, UrlName, UrlTableRow, \
    CheckTableRow, UrlLastCheckTableRow


Pool = pool.SimpleConnectionPool(
    minconn=MINCONN, maxconn=MAXCONN, dsn=DATABASE_URL
)


def make_db_connection(query_func: Callable) -> Any | None:
    """Get connection from pull if it's not passed explicitly and
    give it to wrapped function.
    Return it to the pull after that."""
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
def get_url_id(
        *, conn: Any, url_name: UrlName
) -> tuple[Id | None]:
    """
    Retrieve id of web-site from database
    if it had been already added.
    Else return None
    :param conn: Database connection
    :param url_name: normalized url string
    """

    query = """
    SELECT id
    FROM urls
    WHERE name = %s;"""

    with conn.cursor() as cursor:
        cursor.execute(query,
                       (url_name,))
        url_id_row = cursor.fetchone()

    return url_id_row


@make_db_connection
def get_url_checks(*, conn: Any, url_id: Id) -> list[CheckTableRow]:
    """

    :param conn: Database connection
    :param url_id: url_id int
    :return: return list with all checks of url every check is a TableRow
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

    return raw_checks


@make_db_connection
def get_url(*, conn: Any, url_id: Id) -> UrlTableRow | None:
    """
    By given id
    Return url (id, name, created_at) row from db if exists
    Return empty tuple if it doesn't exist
    :param conn: Database connection
    :param url_id: url id int
    """
    query = """
            SELECT *
            FROM urls
            WHERE id = %s
            """

    with conn.cursor() as cursor:
        cursor.execute(query,
                       (url_id,))
        url_row = cursor.fetchone()

    return url_row


@make_db_connection
def get_all_urls(*, conn: Any) -> list[UrlLastCheckTableRow | None]:
    """
    :param conn: Database connection
    :return: list of all urls (TableRow) in database
    with last checks result and date if presented.
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

    return raw_urls


@make_db_connection
def add_url(*, conn: Any, url_name: UrlName) -> Id:
    """Add url to database. Return id"""

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
        cursor.execute(query,
                       {
                           'url_id': check.url_id,
                           'status_code': check.status_code,
                           'h1': check.h1,
                           'title': check.title,
                           'description': check.description,
                           'created_at': created_at
                       }
                       )


def find_url(url_id: Id) -> Url | None:
    """
    :param url_id: int url id
    :return: Url object by id
    """
    try:
        url_id, name, created_at = get_url(url_id=url_id)
        return Url(id=url_id, name=name, created_at=created_at)
    except TypeError:
        return None


def find_checks(url_id: Id) -> list[Check | None]:
    """
    :param url_id: int url id
    :return: list with Checks of url or with None if there isn't any
    """
    raw_checks = get_url_checks(url_id=url_id)

    checks = [
        Check(
            id=id,
            status_code=status_code,
            h1=h1,
            title=title,
            description=description,
            created_at=created_at
        ) for id,
        status_code,
        h1,
        title,
        description,
        created_at in raw_checks]

    return checks


def find_all_urls_with_last_check() -> list[tuple[Url, Check]]:
    """
    :return: list of tuples with Url and its last Check
    if there isn't last check for url
    Check object will have fields containing None
    """
    raw_urls = get_all_urls()

    listed_urls = [
        (Url(
            id=id, name=name
        ), Check(
            created_at=last_check, status_code=status_code
        )) for id, name, last_check, status_code in raw_urls]

    return listed_urls


def find_url_id(url_name: UrlName) -> Id:
    """Retrieve url id by given url name"""
    url_id_row = get_url_id(url_name=url_name)
    if url_id_row:
        return url_id_row[0]
