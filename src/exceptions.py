class PageLoadError(Exception):
    """Исключение для ошибок загрузки страницы."""


class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""


class DataNotFoundError(Exception):
    """Вызывается при отсутствии ожидаемых данных."""
