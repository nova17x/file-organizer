"""
入力ダイアログ (PyQt6版)
カテゴリとパターンの入力ダイアログ
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt
from typing import Optional, List, Tuple

from .base_window import BaseDialog


class CategoryDialog(BaseDialog):
    """カテゴリ追加/編集ダイアログ"""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        title: str = "カテゴリの追加",
        category: str = "",
        extensions: Optional[List[str]] = None
    ):
        """
        Args:
            parent: 親ウィジェット
            title: ダイアログのタイトル
            category: カテゴリ名（編集時）
            extensions: 拡張子リスト（編集時）
        """
        super().__init__(parent, modal=True)

        self.result = None  # (category, extensions) or None

        # ウィンドウの設定
        self.setWindowTitle(title)
        self.setFixedSize(400, 200)

        # UIの作成
        self._create_widgets(category, extensions or [])

        # 中央に配置
        self.center_on_parent()

    def _create_widgets(self, category: str, extensions: List[str]) -> None:
        """ウィジェットを作成"""
        # メインレイアウト
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # カテゴリ名
        category_label = QLabel("カテゴリ名:")
        layout.addWidget(category_label)

        self.category_edit = QLineEdit()
        self.category_edit.setText(category)
        layout.addWidget(self.category_edit)

        # 拡張子
        extensions_label = QLabel("拡張子 (カンマ区切り):")
        layout.addWidget(extensions_label)

        self.extensions_edit = QLineEdit()
        self.extensions_edit.setText(", ".join(extensions) if extensions else "")
        layout.addWidget(self.extensions_edit)

        # スペーサー
        layout.addStretch()

        # ボタン
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self._on_ok)
        ok_button.setMinimumWidth(80)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setMinimumWidth(80)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Enterキーで確定
        ok_button.setDefault(True)

    def _on_ok(self) -> None:
        """OKボタンが押された時の処理"""
        category = self.category_edit.text().strip()
        extensions_str = self.extensions_edit.text().strip()

        # バリデーション
        if not category:
            QMessageBox.warning(self, "警告", "カテゴリ名を入力してください")
            return

        if not extensions_str:
            QMessageBox.warning(self, "警告", "拡張子を入力してください")
            return

        # 拡張子の処理
        extensions = [ext.strip() for ext in extensions_str.split(",")]
        extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]

        # 結果を設定
        self.result = (category, extensions)
        self.accept()



class PatternDialog(BaseDialog):
    """パターン追加/編集ダイアログ"""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        title: str = "パターンの追加",
        category: str = "",
        pattern: str = ""
    ):
        """
        Args:
            parent: 親ウィジェット
            title: ダイアログのタイトル
            category: カテゴリ名（編集時）
            pattern: 正規表現パターン（編集時）
        """
        super().__init__(parent, modal=True)

        self.result = None  # (category, pattern) or None

        # ウィンドウの設定
        self.setWindowTitle(title)
        self.setFixedSize(400, 200)

        # UIの作成
        self._create_widgets(category, pattern)

        # 中央に配置
        self.center_on_parent()

    def _create_widgets(self, category: str, pattern: str) -> None:
        """ウィジェットを作成"""
        # メインレイアウト
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # カテゴリ名
        category_label = QLabel("カテゴリ名:")
        layout.addWidget(category_label)

        self.category_edit = QLineEdit()
        self.category_edit.setText(category)
        layout.addWidget(self.category_edit)

        # パターン
        pattern_label = QLabel("正規表現パターン:")
        layout.addWidget(pattern_label)

        self.pattern_edit = QLineEdit()
        self.pattern_edit.setText(pattern)
        layout.addWidget(self.pattern_edit)

        # スペーサー
        layout.addStretch()

        # ボタン
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self._on_ok)
        ok_button.setMinimumWidth(80)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setMinimumWidth(80)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Enterキーで確定
        ok_button.setDefault(True)

    def _on_ok(self) -> None:
        """OKボタンが押された時の処理"""
        category = self.category_edit.text().strip()
        pattern = self.pattern_edit.text().strip()

        # バリデーション
        if not category:
            QMessageBox.warning(self, "警告", "カテゴリ名を入力してください")
            return

        if not pattern:
            QMessageBox.warning(self, "警告", "パターンを入力してください")
            return

        # 結果を設定
        self.result = (category, pattern)
        self.accept()

