from urllib.parse import urlparse
from bs4 import BeautifulSoup


def normalize_url(url):
    o = urlparse(url)
    return f'{o.scheme}://{o.netloc}'


def check_page(response):
    status_code = response.status_code

    soup = BeautifulSoup(response.text, 'html.parser')

    return {
        "status_code": status_code,
        "h1": soup.find('h1').text if soup.find('h1') else '',
        "title": soup.title.text if soup.title else '',
        "description": soup.find(
            'meta', attrs={'name': 'description'}
        )['content'] if soup.find(
            'meta', attrs={'name': 'description'}
        ) else ''
    }
