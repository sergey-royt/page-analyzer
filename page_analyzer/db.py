from dotenv import load_dotenv
import psycopg2
from datetime import date

from .settings import DATABASE_URL


load_dotenv()


def connect():
    """"""
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def get_site_id(url):
    with connect().cursor() as cursor:
        cursor.execute(
            """SELECT id
            FROM urls
            WHERE name = %(url)s;""",
            {'url': url})
        try:
            return cursor.fetchone()[0]
        except TypeError:
            return None


def add_url(url):
    """"""
    created_at = str(date.today())
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute("""INSERT INTO urls
        (name, created_at)
        VALUES (%(name)s, %(created_at)s)
        RETURNING id""",
                       {'name': url, 'created_at': created_at})
        url_id = cursor.fetchone()[0]
        conn.commit()
    return url_id


def find_url(id):
    """"""
    with connect().cursor() as cursor:
        cursor.execute("""
        SELECT *
        FROM urls
        WHERE id = %(id)s""", {'id': id})
        row = cursor.fetchone()
    url_id, name, created_at = row
    return {'id': url_id, 'name': name, 'created_at': created_at}


def list_urls():
    """"""
    with connect().cursor() as cursor:
        cursor.execute("""
        SELECT DISTINCT ON (urls.id)
        urls.id,
        urls.name,
        MAX(url_checks.created_at) AS last_check,
        url_checks.status_code
        FROM urls
        LEFT JOIN url_checks ON urls.id = url_checks.url_id
        GROUP BY urls.id, urls.name, url_checks.status_code
        ORDER BY urls.id
        DESC""")
        raw_urls = cursor.fetchall()
    urls = [
        {
            'id': id,
            'name': name,
            'last_check': last_check or '',
            'status_code': status_code or ''
        } for id, name, last_check, status_code in raw_urls
    ]
    return urls


def show_checks(id):
    """"""
    with connect().cursor() as cursor:
        cursor.execute("""
        SELECT id,
        status_code,
        COALESCE(h1, ''),
        COALESCE(title, ''),
        COALESCE(description, ''),
        created_at
        FROM url_checks
        WHERE url_id = %(url_id)s""", {'url_id': id})
        raw_checks = cursor.fetchall()
    checks = [
        {
            'id': id,
            'status_code': status_code,
            'h1': h1,
            'title': title,
            'description': description,
            'created_at': created_at
        } for id,
        status_code,
        h1,
        title,
        description,
        created_at in raw_checks]
    return checks


def add_check(url_id, status_code=None, h1=None, title=None, description=None):
    """"""
    created_at = str(date.today())
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute("""
        INSERT INTO url_checks
        (url_id, status_code, h1, title, description, created_at)
        VALUES (%(url_id)s,
        %(status_code)s,
        %(h1)s,
        %(title)s,
        %(description)s,
        %(created_at)s)""",
                       {
                           'url_id': url_id,
                           'status_code': status_code,
                           'h1': h1,
                           'title': title,
                           'description': description,
                           'created_at': created_at
                       }
                       )
        conn.commit()
