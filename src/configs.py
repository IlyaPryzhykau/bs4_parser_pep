import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import (BASE_DIR, DT_FORMAT, LOG_FORMAT, LOGS_DIR_NAME,
                       LOGS_FILE_NAME, OUTPUT_FILE, OUTPUT_PRETTY)


def configure_argument_parser(available_modes):
    """Конфигурирует парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(description='Парсер документации Python')

    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=(OUTPUT_PRETTY, OUTPUT_FILE),
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging():
    """Настраивает логирование с ротацией файлов."""
    log_dir = BASE_DIR / LOGS_DIR_NAME
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / LOGS_FILE_NAME

    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=10 ** 6, backupCount=5
    )

    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
