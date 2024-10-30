from pathlib import Path

# Основные URL документации и PEP
MAIN_DOC_URL = 'https://docs.python.org/3/'
MAIN_PEP_URL = 'https://peps.python.org/'

# Путь к базовой директории
BASE_DIR = Path(__file__).parent

# Формат даты и времени
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

# Ожидаемые статусы PEP
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}

# Конфигурация логирования
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'

# Форматы вывода данных
OUTPUT_PRETTY = 'pretty'
OUTPUT_FILE = 'file'

# Имена директорий для хранения логов и результатов
LOGS_DIR_NAME = 'logs'
LOGS_FILE_NAME = 'parser.log'
RESULTS_DIR_NAME = 'results'
DOWNLOADS_DIR_NAME = 'downloads'
