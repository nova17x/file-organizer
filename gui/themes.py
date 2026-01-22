"""
テーマシステム
PyQt6アプリケーションのテーマ管理とQSSスタイル定義
"""

from enum import Enum
from typing import Optional


class ThemeType(Enum):
    """テーマの種類"""
    LIGHT = "light"
    DARK = "dark"


class ColorPalette:
    """カラーパレット定義"""

    # ダークテーマカラー
    class Dark:
        # 背景色
        BG_PRIMARY = "#2b2b2b"
        BG_SECONDARY = "#3c3f41"
        BG_TERTIARY = "#4c5052"
        BG_INPUT = "#3c3f41"
        BG_HOVER = "#4c5052"

        # テキスト色
        TEXT_PRIMARY = "#ffffff"
        TEXT_SECONDARY = "#bbbbbb"
        TEXT_DISABLED = "#777777"

        # ボーダー色
        BORDER_PRIMARY = "#555555"
        BORDER_SECONDARY = "#666666"
        BORDER_FOCUS = "#4a90e2"

        # アクセント色
        ACCENT_PRIMARY = "#4a90e2"
        ACCENT_HOVER = "#5a9fe7"
        ACCENT_PRESSED = "#3a80d2"

        # ステータス色
        SUCCESS = "#5cb85c"
        WARNING = "#f0ad4e"
        ERROR = "#d9534f"
        INFO = "#5bc0de"

        # プログレスバー
        PROGRESS_BG = "#3c3f41"
        PROGRESS_CHUNK = "#4a90e2"

    # ライトテーマカラー
    class Light:
        # 背景色
        BG_PRIMARY = "#ffffff"
        BG_SECONDARY = "#f5f5f5"
        BG_TERTIARY = "#e8e8e8"
        BG_INPUT = "#ffffff"
        BG_HOVER = "#e8e8e8"

        # テキスト色
        TEXT_PRIMARY = "#2b2b2b"
        TEXT_SECONDARY = "#555555"
        TEXT_DISABLED = "#bbbbbb"

        # ボーダー色
        BORDER_PRIMARY = "#cccccc"
        BORDER_SECONDARY = "#dddddd"
        BORDER_FOCUS = "#4a90e2"

        # アクセント色
        ACCENT_PRIMARY = "#4a90e2"
        ACCENT_HOVER = "#5a9fe7"
        ACCENT_PRESSED = "#3a80d2"

        # ステータス色
        SUCCESS = "#5cb85c"
        WARNING = "#f0ad4e"
        ERROR = "#d9534f"
        INFO = "#5bc0de"

        # プログレスバー
        PROGRESS_BG = "#f5f5f5"
        PROGRESS_CHUNK = "#4a90e2"


class ThemeManager:
    """テーママネージャークラス"""

    _current_theme: ThemeType = ThemeType.DARK

    @classmethod
    def get_current_theme(cls) -> ThemeType:
        """現在のテーマを取得"""
        return cls._current_theme

    @classmethod
    def set_theme(cls, theme: ThemeType) -> None:
        """テーマを設定"""
        cls._current_theme = theme

    @classmethod
    def get_stylesheet(cls, theme: Optional[ThemeType] = None) -> str:
        """
        指定されたテーマのスタイルシートを取得

        Args:
            theme: テーマタイプ。Noneの場合は現在のテーマを使用

        Returns:
            QSS形式のスタイルシート文字列
        """
        if theme is None:
            theme = cls._current_theme

        if theme == ThemeType.DARK:
            return cls._get_dark_stylesheet()
        else:
            return cls._get_light_stylesheet()

    @classmethod
    def apply_theme(cls, app, theme: ThemeType) -> None:
        """
        アプリケーションにテーマを適用

        Args:
            app: QApplication インスタンス
            theme: 適用するテーマ
        """
        cls.set_theme(theme)
        stylesheet = cls.get_stylesheet(theme)
        app.setStyleSheet(stylesheet)

    @classmethod
    def _get_dark_stylesheet(cls) -> str:
        """ダークテーマのスタイルシート"""
        c = ColorPalette.Dark

        return f"""
            /* メインウィンドウとダイアログ */
            QMainWindow, QDialog {{
                background-color: {c.BG_PRIMARY};
                color: {c.TEXT_PRIMARY};
            }}

            /* ラベル */
            QLabel {{
                color: {c.TEXT_PRIMARY};
                background-color: transparent;
            }}

            /* ボタン */
            QPushButton {{
                background-color: {c.BG_SECONDARY};
                border: 1px solid {c.BORDER_PRIMARY};
                border-radius: 4px;
                padding: 6px 12px;
                color: {c.TEXT_PRIMARY};
                min-height: 20px;
            }}

            QPushButton:hover {{
                background-color: {c.BG_HOVER};
                border-color: {c.BORDER_SECONDARY};
            }}

            QPushButton:pressed {{
                background-color: {c.BG_PRIMARY};
            }}

            QPushButton:disabled {{
                background-color: {c.BG_SECONDARY};
                color: {c.TEXT_DISABLED};
                border-color: {c.BORDER_PRIMARY};
            }}

            /* アクセントボタン */
            QPushButton#accentButton {{
                background-color: {c.ACCENT_PRIMARY};
                border-color: {c.ACCENT_PRIMARY};
                color: {c.TEXT_PRIMARY};
                font-weight: bold;
            }}

            QPushButton#accentButton:hover {{
                background-color: {c.ACCENT_HOVER};
                border-color: {c.ACCENT_HOVER};
            }}

            QPushButton#accentButton:pressed {{
                background-color: {c.ACCENT_PRESSED};
            }}

            /* 入力フィールド */
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {c.BG_INPUT};
                border: 1px solid {c.BORDER_PRIMARY};
                border-radius: 3px;
                padding: 5px;
                color: {c.TEXT_PRIMARY};
                selection-background-color: {c.ACCENT_PRIMARY};
            }}

            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border-color: {c.BORDER_FOCUS};
            }}

            QLineEdit:disabled, QTextEdit:disabled {{
                background-color: {c.BG_SECONDARY};
                color: {c.TEXT_DISABLED};
            }}

            /* コンボボックス */
            QComboBox {{
                background-color: {c.BG_INPUT};
                border: 1px solid {c.BORDER_PRIMARY};
                border-radius: 3px;
                padding: 5px;
                color: {c.TEXT_PRIMARY};
            }}

            QComboBox:hover {{
                border-color: {c.BORDER_SECONDARY};
            }}

            QComboBox:focus {{
                border-color: {c.BORDER_FOCUS};
            }}

            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}

            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {c.TEXT_PRIMARY};
                width: 0;
                height: 0;
            }}

            QComboBox QAbstractItemView {{
                background-color: {c.BG_SECONDARY};
                border: 1px solid {c.BORDER_PRIMARY};
                selection-background-color: {c.ACCENT_PRIMARY};
                color: {c.TEXT_PRIMARY};
            }}

            /* チェックボックスとラジオボタン */
            QCheckBox, QRadioButton {{
                color: {c.TEXT_PRIMARY};
                spacing: 5px;
            }}

            QCheckBox:disabled, QRadioButton:disabled {{
                color: {c.TEXT_DISABLED};
            }}

            QCheckBox::indicator, QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {c.BORDER_PRIMARY};
                border-radius: 2px;
                background-color: {c.BG_INPUT};
            }}

            QRadioButton::indicator {{
                border-radius: 8px;
            }}

            QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
                border-color: {c.BORDER_SECONDARY};
            }}

            QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
                background-color: {c.ACCENT_PRIMARY};
                border-color: {c.ACCENT_PRIMARY};
            }}

            /* プログレスバー */
            QProgressBar {{
                border: 1px solid {c.BORDER_PRIMARY};
                border-radius: 4px;
                background-color: {c.PROGRESS_BG};
                text-align: center;
                color: {c.TEXT_PRIMARY};
                min-height: 20px;
            }}

            QProgressBar::chunk {{
                background-color: {c.PROGRESS_CHUNK};
                border-radius: 3px;
            }}

            /* リストウィジェット */
            QListWidget, QTreeWidget, QTableWidget {{
                background-color: {c.BG_INPUT};
                border: 1px solid {c.BORDER_PRIMARY};
                border-radius: 3px;
                color: {c.TEXT_PRIMARY};
                selection-background-color: {c.ACCENT_PRIMARY};
            }}

            QListWidget::item:hover, QTreeWidget::item:hover, QTableWidget::item:hover {{
                background-color: {c.BG_HOVER};
            }}

            QHeaderView::section {{
                background-color: {c.BG_SECONDARY};
                color: {c.TEXT_PRIMARY};
                border: 1px solid {c.BORDER_PRIMARY};
                padding: 5px;
            }}

            /* タブウィジェット */
            QTabWidget::pane {{
                border: 1px solid {c.BORDER_PRIMARY};
                border-radius: 3px;
                background-color: {c.BG_PRIMARY};
            }}

            QTabBar::tab {{
                background-color: {c.BG_SECONDARY};
                border: 1px solid {c.BORDER_PRIMARY};
                border-bottom: none;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                padding: 6px 12px;
                color: {c.TEXT_SECONDARY};
            }}

            QTabBar::tab:selected {{
                background-color: {c.BG_PRIMARY};
                color: {c.TEXT_PRIMARY};
            }}

            QTabBar::tab:hover:!selected {{
                background-color: {c.BG_HOVER};
            }}

            /* スクロールバー */
            QScrollBar:vertical {{
                background-color: {c.BG_SECONDARY};
                width: 12px;
                margin: 0;
            }}

            QScrollBar::handle:vertical {{
                background-color: {c.BORDER_PRIMARY};
                min-height: 20px;
                border-radius: 6px;
                margin: 2px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {c.BORDER_SECONDARY};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}

            QScrollBar:horizontal {{
                background-color: {c.BG_SECONDARY};
                height: 12px;
                margin: 0;
            }}

            QScrollBar::handle:horizontal {{
                background-color: {c.BORDER_PRIMARY};
                min-width: 20px;
                border-radius: 6px;
                margin: 2px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background-color: {c.BORDER_SECONDARY};
            }}

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
            }}

            /* メニューバー */
            QMenuBar {{
                background-color: {c.BG_SECONDARY};
                color: {c.TEXT_PRIMARY};
                border-bottom: 1px solid {c.BORDER_PRIMARY};
            }}

            QMenuBar::item {{
                padding: 5px 10px;
                background-color: transparent;
            }}

            QMenuBar::item:selected {{
                background-color: {c.BG_HOVER};
            }}

            QMenu {{
                background-color: {c.BG_SECONDARY};
                border: 1px solid {c.BORDER_PRIMARY};
                color: {c.TEXT_PRIMARY};
            }}

            QMenu::item {{
                padding: 5px 30px 5px 10px;
            }}

            QMenu::item:selected {{
                background-color: {c.ACCENT_PRIMARY};
            }}

            /* ステータスバー */
            QStatusBar {{
                background-color: {c.BG_SECONDARY};
                color: {c.TEXT_PRIMARY};
                border-top: 1px solid {c.BORDER_PRIMARY};
            }}

            /* グループボックス */
            QGroupBox {{
                border: 1px solid {c.BORDER_PRIMARY};
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                color: {c.TEXT_PRIMARY};
                font-weight: bold;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                background-color: {c.BG_PRIMARY};
            }}

            /* スピンボックス */
            QSpinBox, QDoubleSpinBox {{
                background-color: {c.BG_INPUT};
                border: 1px solid {c.BORDER_PRIMARY};
                border-radius: 3px;
                padding: 5px;
                color: {c.TEXT_PRIMARY};
            }}

            QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {c.BORDER_FOCUS};
            }}

            /* ツールチップ */
            QToolTip {{
                background-color: {c.BG_SECONDARY};
                border: 1px solid {c.BORDER_PRIMARY};
                color: {c.TEXT_PRIMARY};
                padding: 5px;
            }}
        """

    @classmethod
    def _get_light_stylesheet(cls) -> str:
        """ライトテーマのスタイルシート"""
        c = ColorPalette.Light

        return f"""
            /* メインウィンドウとダイアログ */
            QMainWindow, QDialog {{
                background-color: {c.BG_PRIMARY};
                color: {c.TEXT_PRIMARY};
            }}

            /* ラベル */
            QLabel {{
                color: {c.TEXT_PRIMARY};
                background-color: transparent;
            }}

            /* ボタン */
            QPushButton {{
                background-color: {c.BG_SECONDARY};
                border: 1px solid {c.BORDER_PRIMARY};
                border-radius: 4px;
                padding: 6px 12px;
                color: {c.TEXT_PRIMARY};
                min-height: 20px;
            }}

            QPushButton:hover {{
                background-color: {c.BG_HOVER};
                border-color: {c.BORDER_SECONDARY};
            }}

            QPushButton:pressed {{
                background-color: {c.BG_TERTIARY};
            }}

            QPushButton:disabled {{
                background-color: {c.BG_SECONDARY};
                color: {c.TEXT_DISABLED};
                border-color: {c.BORDER_PRIMARY};
            }}

            /* アクセントボタン */
            QPushButton#accentButton {{
                background-color: {c.ACCENT_PRIMARY};
                border-color: {c.ACCENT_PRIMARY};
                color: #ffffff;
                font-weight: bold;
            }}

            QPushButton#accentButton:hover {{
                background-color: {c.ACCENT_HOVER};
                border-color: {c.ACCENT_HOVER};
            }}

            QPushButton#accentButton:pressed {{
                background-color: {c.ACCENT_PRESSED};
            }}

            /* 入力フィールド */
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {c.BG_INPUT};
                border: 1px solid {c.BORDER_PRIMARY};
                border-radius: 3px;
                padding: 5px;
                color: {c.TEXT_PRIMARY};
                selection-background-color: {c.ACCENT_PRIMARY};
            }}

            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border-color: {c.BORDER_FOCUS};
            }}

            QLineEdit:disabled, QTextEdit:disabled {{
                background-color: {c.BG_SECONDARY};
                color: {c.TEXT_DISABLED};
            }}

            /* コンボボックス */
            QComboBox {{
                background-color: {c.BG_INPUT};
                border: 1px solid {c.BORDER_PRIMARY};
                border-radius: 3px;
                padding: 5px;
                color: {c.TEXT_PRIMARY};
            }}

            QComboBox:hover {{
                border-color: {c.BORDER_SECONDARY};
            }}

            QComboBox:focus {{
                border-color: {c.BORDER_FOCUS};
            }}

            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}

            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {c.TEXT_PRIMARY};
                width: 0;
                height: 0;
            }}

            QComboBox QAbstractItemView {{
                background-color: {c.BG_PRIMARY};
                border: 1px solid {c.BORDER_PRIMARY};
                selection-background-color: {c.ACCENT_PRIMARY};
                selection-color: #ffffff;
                color: {c.TEXT_PRIMARY};
            }}

            /* チェックボックスとラジオボタン */
            QCheckBox, QRadioButton {{
                color: {c.TEXT_PRIMARY};
                spacing: 5px;
            }}

            QCheckBox:disabled, QRadioButton:disabled {{
                color: {c.TEXT_DISABLED};
            }}

            QCheckBox::indicator, QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {c.BORDER_PRIMARY};
                border-radius: 2px;
                background-color: {c.BG_INPUT};
            }}

            QRadioButton::indicator {{
                border-radius: 8px;
            }}

            QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
                border-color: {c.BORDER_SECONDARY};
            }}

            QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
                background-color: {c.ACCENT_PRIMARY};
                border-color: {c.ACCENT_PRIMARY};
            }}

            /* プログレスバー */
            QProgressBar {{
                border: 1px solid {c.BORDER_PRIMARY};
                border-radius: 4px;
                background-color: {c.PROGRESS_BG};
                text-align: center;
                color: {c.TEXT_PRIMARY};
                min-height: 20px;
            }}

            QProgressBar::chunk {{
                background-color: {c.PROGRESS_CHUNK};
                border-radius: 3px;
            }}

            /* リストウィジェット */
            QListWidget, QTreeWidget, QTableWidget {{
                background-color: {c.BG_INPUT};
                border: 1px solid {c.BORDER_PRIMARY};
                border-radius: 3px;
                color: {c.TEXT_PRIMARY};
                selection-background-color: {c.ACCENT_PRIMARY};
                selection-color: #ffffff;
            }}

            QListWidget::item:hover, QTreeWidget::item:hover, QTableWidget::item:hover {{
                background-color: {c.BG_HOVER};
            }}

            QHeaderView::section {{
                background-color: {c.BG_SECONDARY};
                color: {c.TEXT_PRIMARY};
                border: 1px solid {c.BORDER_PRIMARY};
                padding: 5px;
            }}

            /* タブウィジェット */
            QTabWidget::pane {{
                border: 1px solid {c.BORDER_PRIMARY};
                border-radius: 3px;
                background-color: {c.BG_PRIMARY};
            }}

            QTabBar::tab {{
                background-color: {c.BG_SECONDARY};
                border: 1px solid {c.BORDER_PRIMARY};
                border-bottom: none;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                padding: 6px 12px;
                color: {c.TEXT_SECONDARY};
            }}

            QTabBar::tab:selected {{
                background-color: {c.BG_PRIMARY};
                color: {c.TEXT_PRIMARY};
            }}

            QTabBar::tab:hover:!selected {{
                background-color: {c.BG_HOVER};
            }}

            /* スクロールバー */
            QScrollBar:vertical {{
                background-color: {c.BG_SECONDARY};
                width: 12px;
                margin: 0;
            }}

            QScrollBar::handle:vertical {{
                background-color: {c.BORDER_PRIMARY};
                min-height: 20px;
                border-radius: 6px;
                margin: 2px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {c.BORDER_SECONDARY};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}

            QScrollBar:horizontal {{
                background-color: {c.BG_SECONDARY};
                height: 12px;
                margin: 0;
            }}

            QScrollBar::handle:horizontal {{
                background-color: {c.BORDER_PRIMARY};
                min-width: 20px;
                border-radius: 6px;
                margin: 2px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background-color: {c.BORDER_SECONDARY};
            }}

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
            }}

            /* メニューバー */
            QMenuBar {{
                background-color: {c.BG_SECONDARY};
                color: {c.TEXT_PRIMARY};
                border-bottom: 1px solid {c.BORDER_PRIMARY};
            }}

            QMenuBar::item {{
                padding: 5px 10px;
                background-color: transparent;
            }}

            QMenuBar::item:selected {{
                background-color: {c.BG_HOVER};
            }}

            QMenu {{
                background-color: {c.BG_PRIMARY};
                border: 1px solid {c.BORDER_PRIMARY};
                color: {c.TEXT_PRIMARY};
            }}

            QMenu::item {{
                padding: 5px 30px 5px 10px;
            }}

            QMenu::item:selected {{
                background-color: {c.ACCENT_PRIMARY};
                color: #ffffff;
            }}

            /* ステータスバー */
            QStatusBar {{
                background-color: {c.BG_SECONDARY};
                color: {c.TEXT_PRIMARY};
                border-top: 1px solid {c.BORDER_PRIMARY};
            }}

            /* グループボックス */
            QGroupBox {{
                border: 1px solid {c.BORDER_PRIMARY};
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                color: {c.TEXT_PRIMARY};
                font-weight: bold;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                background-color: {c.BG_PRIMARY};
            }}

            /* スピンボックス */
            QSpinBox, QDoubleSpinBox {{
                background-color: {c.BG_INPUT};
                border: 1px solid {c.BORDER_PRIMARY};
                border-radius: 3px;
                padding: 5px;
                color: {c.TEXT_PRIMARY};
            }}

            QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {c.BORDER_FOCUS};
            }}

            /* ツールチップ */
            QToolTip {{
                background-color: {c.BG_SECONDARY};
                border: 1px solid {c.BORDER_PRIMARY};
                color: {c.TEXT_PRIMARY};
                padding: 5px;
            }}
        """
