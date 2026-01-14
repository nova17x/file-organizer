"""
ファイル分類エンジン
ファイルを様々な基準で分類
"""

import os
import re
from datetime import datetime
from typing import Optional, Dict, List


class FileClassifier:
    """ファイルを分類するクラス"""

    # デフォルトの拡張子カテゴリ
    DEFAULT_CATEGORIES = {
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

    def __init__(self, custom_categories: Optional[Dict[str, List[str]]] = None):
        """
        Args:
            custom_categories: カスタムカテゴリ辞書（カテゴリ名: [拡張子リスト]）
        """
        self.categories = self.DEFAULT_CATEGORIES.copy()
        if custom_categories:
            self.categories.update(custom_categories)

    def classify_by_extension(self, file_path: str) -> str:
        """
        拡張子に基づいてファイルを分類

        Args:
            file_path: ファイルのパス

        Returns:
            カテゴリ名（該当なしの場合は "Others"）
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        for category, extensions in self.categories.items():
            if ext in extensions:
                return category

        return "Others"

    def classify_by_date(self, file_path: str, mode: str = 'modified',
                        date_format: str = '%Y/%m') -> Optional[str]:
        """
        日付に基づいてファイルを分類

        Args:
            file_path: ファイルのパス
            mode: 'created' (作成日) または 'modified' (更新日)
            date_format: 日付フォルダの形式（例: '%Y/%m' → '2026/01'）

        Returns:
            日付フォルダのパス（例: "2026/01"）。エラー時はNone
        """
        try:
            if not os.path.exists(file_path):
                return None

            if mode == 'created':
                # 作成日時を取得
                timestamp = os.path.getctime(file_path)
            elif mode == 'modified':
                # 更新日時を取得
                timestamp = os.path.getmtime(file_path)
            else:
                print(f"警告: 不明なモード '{mode}'。'modified'を使用します。")
                timestamp = os.path.getmtime(file_path)

            date = datetime.fromtimestamp(timestamp)
            return date.strftime(date_format)

        except Exception as e:
            print(f"エラー: 日付の取得に失敗しました: {file_path} - {e}")
            return None

    def classify_by_size(self, file_path: str,
                        thresholds: Optional[Dict[str, int]] = None) -> str:
        """
        ファイルサイズに基づいて分類

        Args:
            file_path: ファイルのパス
            thresholds: サイズの閾値辞書（バイト単位）
                       デフォルト: {"Small": 1MB, "Medium": 100MB, "Large": 1GB}

        Returns:
            サイズカテゴリ名
        """
        if thresholds is None:
            thresholds = {
                "Small": 1 * 1024 * 1024,        # 1MB
                "Medium": 100 * 1024 * 1024,     # 100MB
                "Large": 1024 * 1024 * 1024,     # 1GB
            }

        try:
            file_size = os.path.getsize(file_path)

            # サイズを昇順でソートした閾値で判定
            sorted_thresholds = sorted(thresholds.items(), key=lambda x: x[1])

            for category, threshold in sorted_thresholds:
                if file_size <= threshold:
                    return category

            # すべての閾値を超える場合
            return "VeryLarge"

        except Exception as e:
            print(f"エラー: ファイルサイズの取得に失敗しました: {file_path} - {e}")
            return "Unknown"

    def classify_by_pattern(self, file_path: str,
                           patterns: Dict[str, str]) -> Optional[str]:
        """
        ファイル名のパターンマッチングで分類

        Args:
            file_path: ファイルのパス
            patterns: パターン辞書（カテゴリ名: 正規表現パターン）
                     例: {"Screenshots": r"^screenshot_.*", "Camera": r"^IMG_.*"}

        Returns:
            マッチしたカテゴリ名。マッチしない場合はNone
        """
        filename = os.path.basename(file_path)

        for category, pattern in patterns.items():
            try:
                if re.match(pattern, filename, re.IGNORECASE):
                    return category
            except re.error as e:
                print(f"警告: 不正な正規表現パターン '{pattern}': {e}")
                continue

        return None

    def classify_multi(self, file_path: str, rules: List[Dict]) -> Dict[str, str]:
        """
        複数のルールを適用してファイルを分類

        Args:
            file_path: ファイルのパス
            rules: ルールのリスト
                  各ルールは {'type': 'extension'|'date'|'size'|'pattern', ...} の形式

        Returns:
            分類結果の辞書 {'extension': 'Images', 'date': '2026/01', ...}
        """
        results = {}

        for rule in rules:
            rule_type = rule.get('type')

            if rule_type == 'extension':
                results['extension'] = self.classify_by_extension(file_path)

            elif rule_type == 'date':
                mode = rule.get('mode', 'modified')
                date_format = rule.get('format', '%Y/%m')
                date_folder = self.classify_by_date(file_path, mode, date_format)
                if date_folder:
                    results['date'] = date_folder

            elif rule_type == 'size':
                thresholds = rule.get('thresholds')
                results['size'] = self.classify_by_size(file_path, thresholds)

            elif rule_type == 'pattern':
                patterns = rule.get('patterns', {})
                category = self.classify_by_pattern(file_path, patterns)
                if category:
                    results['pattern'] = category

        return results

    def get_destination_path(self, file_path: str, base_dir: str,
                           classification: Dict[str, str],
                           priority: Optional[List[str]] = None) -> str:
        """
        分類結果に基づいて目的地のパスを生成

        Args:
            file_path: ファイルのパス
            base_dir: 整理先のベースディレクトリ
            classification: classify_multi()の結果
            priority: 分類の優先順位リスト（例: ['pattern', 'extension', 'date']）

        Returns:
            目的地のフルパス
        """
        if priority is None:
            priority = ['pattern', 'extension', 'date', 'size']

        # 優先順位に従ってパスコンポーネントを構築
        path_components = [base_dir]

        for key in priority:
            if key in classification:
                path_components.append(classification[key])

        # ファイル名を追加
        filename = os.path.basename(file_path)
        path_components.append(filename)

        return os.path.join(*path_components)

    def add_category(self, category_name: str, extensions: List[str]) -> None:
        """
        カスタムカテゴリを追加

        Args:
            category_name: カテゴリ名
            extensions: 拡張子のリスト
        """
        self.categories[category_name] = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}'
                                         for ext in extensions]

    def remove_category(self, category_name: str) -> bool:
        """
        カテゴリを削除

        Args:
            category_name: 削除するカテゴリ名

        Returns:
            成功したらTrue、存在しない場合はFalse
        """
        if category_name in self.categories:
            del self.categories[category_name]
            return True
        return False

    def get_categories(self) -> Dict[str, List[str]]:
        """
        現在のカテゴリ設定を取得

        Returns:
            カテゴリ辞書のコピー
        """
        return self.categories.copy()
