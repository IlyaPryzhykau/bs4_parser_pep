import re
from urllib.parse import urljoin
import logging

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from constants import BASE_DIR, MAIN_DOC_URL, MAIN_PEP_URL, EXPECTED_STATUS
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response, find_tag, find_all_tag


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')

    response = get_response(session, whats_new_url)
    if response is None:
        # Если основная страница не загрузится, программа закончит работу.
        return

    soup = BeautifulSoup(response.text, 'lxml')

    main_div = find_tag(
        soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all('li', attrs={
        'class': 'toctree-l1'})

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор'), ]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')

        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)

        response = get_response(session, version_link)
        if response is None:
            # Если страница не загрузится, программа
            # перейдёт к следующей ссылке.
            continue

        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return

    soup = BeautifulSoup(response.text, 'lxml')

    sidebar = find_tag(soup, 'div', class_='sphinxsidebarwrapper')
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')

    results = []
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')

    response = get_response(session, downloads_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, 'lxml')

    table_tag = find_tag(soup, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)

    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    peps_url = urljoin(MAIN_PEP_URL, '#numerical-index')

    response = get_response(session, peps_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, 'lxml')
    tables = find_all_tag(soup, 'table',
                          {'class': 'pep-zero-table docutils align-default'})

    result_dict = {}

    for table in tables:
        rows = find_all_tag(table, 'tr', {'class': 'row-even'})

        for row in rows:
            abbr_tag = row.find('abbr')
            table_pep_status = abbr_tag.get_text(strip=True) \
                if abbr_tag and 'title' in abbr_tag.attrs else None

            a_tag = row.find('a', {'class': 'pep reference internal'})
            href = a_tag['href']

            pep_url = urljoin(MAIN_PEP_URL, href)
            response = get_response(session, pep_url)
            if response is None:
                return

            soup = BeautifulSoup(response.text, 'lxml')
            pep_info = find_tag(soup, 'dl',
                                {'class': 'rfc2822 field-list simple'})

            pep_info_list = find_all_tag(pep_info, 'abbr')
            pep_status = pep_info_list[0].get_text(strip=True)
            pep_type = pep_info_list[1].get_text(strip=True)

            result_dict[pep_status] = result_dict.get(pep_status, 0) + 1

            if not table_pep_status or len(table_pep_status) < 2:
                logging.info(f'Несовпадающие статусы: {pep_url} \n'
                             f'Статус в карточке: Some unknown status \n'
                             f'Ожидаемые статусы: {pep_type, pep_status}')
            elif pep_status not in EXPECTED_STATUS[table_pep_status[1]]:
                logging.info(f'Несовпадающие статусы: {pep_url} \n'
                             f'Статус в карточке: '
                             f'{EXPECTED_STATUS[table_pep_status[1]]} \n'
                             f'Ожидаемые статусы: {[pep_type, pep_status]}')

        result = list(result_dict.items())

    header = [('Статус', 'Количество')]
    total = [('Total', sum(result_dict.values()))]
    result_list = header + result + total

    return result_list


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    # Запускаем функцию с конфигурацией логов.
    configure_logging()
    # Отмечаем в логах момент запуска программы.
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()

    # Логируем переданные аргументы командной строки.
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    # Сохраняем результат вызова функции в переменную results.
    results = MODE_TO_FUNCTION[parser_mode](session)

    # Если из функции вернулись какие-то результаты,
    if results is not None:
        # передаём их в функцию вывода вместе с аргументами командной строки.
        control_output(results, args)

    # Логируем завершение работы парсера.
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
