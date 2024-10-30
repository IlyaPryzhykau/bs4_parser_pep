import logging

from requests import RequestException
from bs4 import BeautifulSoup

from exceptions import PageLoadError, ParserFindTagException


def get_response(session, url, encoding='utf-8'):
    """Получает ответ от указанного URL с заданной кодировкой."""
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException as e:
        raise PageLoadError(f"Ошибка при загрузке страницы {url}: {e}")


def fetch_soup(session, url, encoding='utf-8', parser='lxml'):
    """Получает и парсит HTML-страницу по заданному URL."""
    response = get_response(session, url, encoding)

    return BeautifulSoup(response.text, parser)


def find_tag(soup, tag, attrs=None):
    """Находит первый тег в soup с заданными атрибутами."""
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def find_all_tag(soup, tag, attrs=None):
    """ Находит все теги в soup с заданными атрибутами."""
    searched_tag = soup.find_all(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
