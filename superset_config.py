import os

SECRET_KEY = "uLyvDzQ/86EUNGBq1anSdHGtlnKaHzRNhDuL0M399aQJ3cxWqCx2pT2/"

# Разрешаем загрузку CSV и Excel
ENABLE_CSV_UPLOAD = True
ENABLE_EXCEL_UPLOAD = True
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# Папка, куда временно складываются загружаемые файлы
CSV_TO_HIVE_UPLOAD_DIRECTORY = '/tmp/superset_uploads/'

# Включаем флаги в интерфейсе
FEATURE_FLAGS = {
    "ENABLE_CSV_UPLOAD": True,
    "ENABLE_EXCEL_UPLOAD": True,
}

# Разрешаем небезопасные подключения (чтобы работал SQLite)
PREVENT_UNSAFE_DB_CONNECTIONS = False
