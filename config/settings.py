"""
アプリケーション設定
デフォルト設定とアプリケーション定数
"""

import os

# アプリケーション情報
APP_NAME = "File Organizer"
APP_VERSION = "1.0.0"
APP_AUTHOR = "File Organizer Team"

# ディレクトリ設定
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RULES_DIR = os.path.join(DATA_DIR, "rules")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
BACKUPS_DIR = os.path.join(DATA_DIR, "backups")

# ログ設定
LOG_RETENTION_DAYS = 30  # ログの保持日数
MAX_LOG_FILES = 100      # 最大ログファイル数

# バックアップ設定
BACKUP_RETENTION_COUNT = 5  # 保持するバックアップの数
AUTO_BACKUP = True          # 自動バックアップを有効にする

# ファイル整理設定
DEFAULT_OPERATION_MODE = "move"  # デフォルトの操作モード（move または copy）
SKIP_EXISTING_FILES = True       # 既存ファイルをスキップするか
SKIP_HIDDEN_FILES = True         # 隠しファイルをスキップするか

# ハッシュ計算設定
HASH_ALGORITHM = "sha256"        # 使用するハッシュアルゴリズム
HASH_CHUNK_SIZE = 8192           # ハッシュ計算時のチャンクサイズ（バイト）
USE_QUICK_SCAN = True            # 高速スキャンを使用するか

# フォルダ監視設定
WATCH_RECURSIVE = True           # サブディレクトリも監視するか
WATCH_DELAY = 2.0               # ファイル作成後の待機時間（秒）

# GUI設定
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
THEME = "default"                # GUIテーマ

# ファイルサイズ閾値（バイト単位）
SIZE_THRESHOLDS = {
    "Small": 1 * 1024 * 1024,        # 1MB
    "Medium": 100 * 1024 * 1024,     # 100MB
    "Large": 1024 * 1024 * 1024,     # 1GB
}

# デフォルト拡張子カテゴリ
DEFAULT_EXTENSION_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".tif"],
    "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".pages"],
    "Spreadsheets": [".xls", ".xlsx", ".csv", ".ods", ".numbers"],
    "Presentations": [".ppt", ".pptx", ".odp", ".key"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "Code": [".py", ".js", ".java", ".cpp", ".c", ".h", ".cs", ".php", ".rb", ".go", ".rs", ".swift"],
    "Web": [".html", ".htm", ".css", ".xml", ".json", ".yaml", ".yml"],
    "Executables": [".exe", ".msi", ".dmg", ".app", ".deb", ".rpm"],
    "Databases": [".db", ".sqlite", ".sql", ".mdb"],
}

# デフォルトファイル名パターン
DEFAULT_PATTERNS = {
    "Screenshots": r"^screenshot[_-].*",
    "Camera": r"^(IMG|DSC|DCIM)[_-].*",
    "Downloads": r"^download.*",
}

# 日付フォーマット
DEFAULT_DATE_FORMAT = "%Y/%m"  # 年/月
DATE_FORMAT_OPTIONS = [
    "%Y/%m",         # 2026/01
    "%Y/%m/%d",      # 2026/01/14
    "%Y",            # 2026
    "%Y-%m",         # 2026-01
    "%Y-%m-%d",      # 2026-01-14
]

# 除外するファイル名パターン
EXCLUDED_PATTERNS = [
    r"^\..*",              # 隠しファイル
    r".*\.tmp$",           # 一時ファイル
    r".*\.temp$",
    r".*\.crdownload$",    # Chrome ダウンロード中
    r".*\.part$",          # 部分ダウンロード
]

# 除外するファイル名
EXCLUDED_FILES = [
    "Thumbs.db",
    "desktop.ini",
    ".DS_Store",
    ".gitkeep",
]

# 除外するディレクトリ名
EXCLUDED_DIRECTORIES = [
    ".git",
    ".svn",
    "node_modules",
    "__pycache__",
    "venv",
    ".venv",
]

# パフォーマンス設定
MAX_WORKERS = 4              # 並列処理の最大ワーカー数
PROGRESS_UPDATE_INTERVAL = 1  # 進捗更新の間隔（秒）

# デバッグ設定
DEBUG = False
VERBOSE = True


def ensure_directories() -> None:
    """必要なディレクトリが存在することを確認"""
    directories = [
        DATA_DIR,
        RULES_DIR,
        LOGS_DIR,
        BACKUPS_DIR,
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def get_default_rule() -> dict:
    """デフォルトのルール設定を取得"""
    return {
        "name": "Default Rule",
        "version": "1.0",
        "description": "デフォルトのファイル整理ルール",
        "priority": ["pattern", "extension", "date"],
        "rules": [
            {
                "type": "extension",
                "enabled": True,
                "categories": DEFAULT_EXTENSION_CATEGORIES
            },
            {
                "type": "date",
                "enabled": True,
                "mode": "modified",
                "format": DEFAULT_DATE_FORMAT
            },
            {
                "type": "pattern",
                "enabled": True,
                "patterns": DEFAULT_PATTERNS
            }
        ]
    }


# 初期化時にディレクトリを作成
ensure_directories()
