from flask import Flask, \
    render_template, \
    request, \
    flash, \
    get_flashed_messages, \
    url_for, \
    redirect
import requests
from dotenv import load_dotenv
from validators import url as validator

import page_analyzer.db as db
from .settings import SECRET_KEY
from .utils import normalize_url, get_accessibility_content
from .models import Url


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/')
def index():
    """Render index page"""
    return render_template('index.html')


@app.post('/urls')
def add_url():
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
            messages=get_flashed_messages(with_categories=True)), 422

    id = db.get_site_id(url)
    if id:
        flash('Страница уже существует', 'info')
        return redirect(url_for('show_url_info', id=id))

    url_id = db.add_url(url)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('show_url_info', id=url_id))


@app.route('/urls/<int:id>')
def show_url_info(id: int):
    """Show url info: id, name, creation date, checks"""
    url = Url(**db.find_url_info(id))
    checks = db.show_checks(id)
    messages = get_flashed_messages(with_categories=True)
    return render_template('show_url.html',
                           url=url,
                           checks=checks,
                           messages=messages
                           )


@app.get('/urls')
def show_urls():
    """Render page with list of urls"""
    urls = db.list_urls()
    return render_template('list_urls.html', urls=urls)


@app.post('/urls/<int:id>/checks')
def initialize_check(id: int):
    """
    Check the SEO effectiveness of web-page:
    Make request to it and check following features:
    Status code, h1 header, title and description
    ===============================================
    Add the check result to database
    """
    url = db.find_url_info(id)['name']

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('show_url', id=id))

    status_code = response.status_code

    accessibility_data = get_accessibility_content(response)

    db.add_check(
        url_id=id,
        status_code=status_code,
        **accessibility_data
    )

    flash('Страница успешно проверена', 'success')

    return redirect(url_for('show_url_info', id=id))
