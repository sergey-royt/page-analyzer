from dotenv import load_dotenv
import psycopg2
import os
from datetime import date

load_dotenv()


def connect():
    database = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(database)
    return conn


def is_url_in_db(url):
    with connect().cursor() as cursor:
        cursor.execute(
            """SELECT id
            FROM urls
            WHERE name = %(url)s;""",
            {'url': url})
        id = cursor.fetchone()
        if id:
            return id[0]
        else:
            return False


def add_url(url):
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
    with connect().cursor() as cursor:
        cursor.execute("""
        SELECT * 
        FROM urls
        WHERE id = %(id)s""", {'id': id})
        row = cursor.fetchone()
    url_id, name, created_at = row
    return {'id': url_id, 'name': name, 'created_at': created_at}


def list_urls():
    with connect().cursor() as cursor:
        cursor.execute("""
        SELECT *
        FROM urls
        ORDER BY id
        DESC;""")
        raw_urls = cursor.fetchall()
    urls = [{'id': id, 'name': name, 'created_at': created_at} for id, name, created_at in raw_urls]
    return urls
