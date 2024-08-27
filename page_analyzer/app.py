from flask import Flask, \
    render_template, \
    request, \
    flash, \
    get_flashed_messages, \
    url_for, \
    redirect
import requests
import os
from dotenv import load_dotenv
from validators import url as validator
from urllib.parse import urlparse
from bs4 import BeautifulSoup

import page_analyzer.db as db
from settings import SECRET_KEY


app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def add_url():
    raw_url = request.form.get('url')
    url = normalize(raw_url)

    if not validator(url):
        flash('Некорректный URL', 'danger')
        return render_template(
            'index.html',
            messages=get_flashed_messages(with_categories=True)), 422

    id = db.is_url_in_db(url)
    if id:
        flash('Страница уже существует', 'info')
        return redirect(url_for('show_url', id=id))

    else:
        url_id = db.add_url(url)
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('show_url', id=url_id))


@app.route('/urls/<int:id>')
def show_url(id):
    url = db.find_url(id)
    checks = db.show_checks(id)
    messages = get_flashed_messages(with_categories=True)
    return render_template('show_url.html',
                           url=url,
                           checks=checks,
                           messages=messages
                           )


@app.get('/urls')
def show_urls():
    urls = db.list_urls()
    return render_template('list_urls.html', urls=urls)


@app.post('/urls/<int:id>/checks')
def initialize_check(id):
    url = db.find_url(id)['name']

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('show_url', id=id))
    status_code = response.status_code

    soup = BeautifulSoup(response.text, 'html.parser')
    h1 = soup.find('h1').text if soup.find('h1') else ''
    title = soup.title.text if soup.title else ''
    description = soup.find(
        'meta',
        {'name': 'description'}
    ).get('content') if soup.find(
        'meta',
        {'name': 'description'}
    ) else ''
    db.add_check(
        url_id=id,
        status_code=status_code,
        h1=h1,
        title=title,
        description=description
    )
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('show_url', id=id))


def normalize(url):
    o = urlparse(url)
    return f'{o.scheme}://{o.netloc}'
