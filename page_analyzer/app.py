from flask import Flask, \
    render_template, \
    request, \
    flash, \
    get_flashed_messages, \
    url_for, \
    redirect
import requests
from requests import Response
from validators import url as validator
from http import HTTPStatus

import page_analyzer.db as db
from .settings import SECRET_KEY
from .utils import normalize_url, get_accessibility_content
from .models import Check


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/')
def index() -> str:
    """Render index page"""
    return render_template('index.html')


@app.post('/urls')
def add_url() -> str | tuple[str, int] | Response:
    """
    Validate url from recieved form
    Add it to database in case it has not been added yet.
    Add flash messages to response
    """

    raw_url = request.form.get('url')
    url = normalize_url(raw_url)

    if not validator(url):
        flash('Некорректный URL', 'danger')
        return render_template(
            'index.html',
            messages=get_flashed_messages(with_categories=True)), \
            HTTPStatus.UNPROCESSABLE_ENTITY

    url_id = db.find_url_id(url_name=url)
    if url_id:
        flash('Страница уже существует', 'info')
        return redirect(url_for('show_url_info', id=url_id))

    url_id = db.add_url(url_name=url)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('show_url_info', id=url_id))


@app.route('/urls/<int:id>')
def show_url_info(id: int) -> str | tuple[str, int]:
    """Show url info: id, name, creation date, checks"""
    url = db.find_url(id)
    if url:
        checks = db.find_checks(id)
        messages = get_flashed_messages(with_categories=True)
        return render_template('show_url.html',
                               url=url,
                               checks=checks,
                               messages=messages
                               )
    return render_template('404.html'), HTTPStatus.NOT_FOUND


@app.get('/urls')
def show_urls() -> str:
    """Render page with list of urls with last check"""
    urls_data = db.find_all_urls_with_last_check()
    return render_template('list_urls.html', urls_data=urls_data)


@app.post('/urls/<int:id>/checks')
def initialize_check(id: int) -> Response:
    """
    Check the SEO effectiveness of web-page:
    Make request to it and check following features:
    Status code, h1 header, title and description
    ===============================================
    Add the check result to database
    """
    url = db.find_url(id)

    try:
        response = requests.get(url.name)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('show_url_info', id=id))

    accessibility_data = get_accessibility_content(response)

    check = Check(url_id=id, **accessibility_data)

    db.add_check(check=check)

    flash('Страница успешно проверена', 'success')

    return redirect(url_for('show_url_info', id=id))
