"""
進捗表示ダイアログ (PyQt6版)
ファイル整理の進捗状況を表示
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton,
    QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Optional

from .base_window import BaseDialog


class ProgressDialog(BaseDialog):
    """進捗状況を表示するダイアログ"""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        title: str = "処理中",
        total_items: int = 100,
        cancelable: bool = True
    ):
        """
        Args:
            parent: 親ウィジェット
            title: ダイアログのタイトル
            total_items: 処理する総アイテム数
            cancelable: キャンセル可能かどうか
        """
        super().__init__(parent, modal=True)

        self.total_items = total_items
        self.current_item = 0
        self.is_cancelled = False
        self.cancelable = cancelable

        # ウィンドウの設定
        self.setWindowTitle(title)
        self.setFixedSize(500, 200)

        # UIの作成
        self._create_widgets()

        # 中央に配置
        self.center_on_parent()

    def _create_widgets(self) -> None:
        """ウィジェットを作成"""
        # メインレイアウト
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # タイトルラベル
        self.title_label = QLabel("処理を実行中...")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # ステータスラベル
        self.status_label = QLabel("準備中...")
        status_font = QFont()
        status_font.setPointSize(10)
        self.status_label.setFont(status_font)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.total_items)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumWidth(400)
        layout.addWidget(self.progress_bar)

        # 進捗テキスト（例: 50/100 (50.0%)）
        self.progress_text = QLabel(f"0 / {self.total_items}")
        progress_font = QFont()
        progress_font.setPointSize(9)
        self.progress_text.setFont(progress_font)
        self.progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_text)

        # スペーサー
        layout.addStretch()

        # キャンセルボタン
        if self.cancelable:
            self.cancel_button = QPushButton("キャンセル")
            self.cancel_button.clicked.connect(self._on_cancel)
            self.cancel_button.setMinimumHeight(30)
            layout.addWidget(self.cancel_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def update_progress(self, current: int, message: str = "") -> None:
        """
        進捗を更新

        Args:
            current: 現在の進捗（処理したアイテム数）
            message: 表示するメッセージ
        """
        self.current_item = current

        # プログレスバーを更新
        self.progress_bar.setValue(current)

        # 進捗テキストを更新
        percentage = (current / self.total_items * 100) if self.total_items > 0 else 0
        self.progress_text.setText(f"{current} / {self.total_items} ({percentage:.1f}%)")

        # メッセージを更新
        if message:
            self.status_label.setText(message)

        # UIを更新
        self.repaint()

    def set_status(self, status_text: str) -> None:
        """
        ステータステキストを設定

        Args:
            status_text: 表示するステータス
        """
        self.status_label.setText(status_text)
        self.repaint()

    def set_title(self, title_text: str) -> None:
        """
        タイトルテキストを設定

        Args:
            title_text: 表示するタイトル
        """
        self.title_label.setText(title_text)
        self.repaint()

    def complete(self, message: str = "完了しました") -> None:
        """
        処理完了を表示

        Args:
            message: 完了メッセージ
        """
        self.progress_bar.setValue(self.total_items)
        self.status_label.setText(message)

        if self.cancelable and hasattr(self, 'cancel_button'):
            self.cancel_button.setText("閉じる")
            self.cancel_button.clicked.disconnect()
            self.cancel_button.clicked.connect(self.close)

        self.repaint()

    def cancel_operation(self) -> None:
        """操作をキャンセル"""
        self.is_cancelled = True

    def _on_cancel(self) -> None:
        """キャンセルボタンが押された時の処理"""
        self.is_cancelled = True
        if hasattr(self, 'cancel_button'):
            self.cancel_button.setEnabled(False)
        self.status_label.setText("キャンセル中...")
        self.repaint()

    def closeEvent(self, event) -> None:
        """ウィンドウを閉じようとした時の処理"""
        if self.cancelable and not self.is_cancelled:
            self._on_cancel()
            event.ignore()
        else:
            event.accept()


class IndeterminateProgressDialog(BaseDialog):
    """不定進捗を表示するダイアログ（処理数が不明な場合）"""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        title: str = "処理中",
        message: str = "処理を実行中..."
    ):
        """
        Args:
            parent: 親ウィジェット
            title: ダイアログのタイトル
            message: 表示するメッセージ
        """
        super().__init__(parent, modal=True)

        # ウィンドウの設定
        self.setWindowTitle(title)
        self.setFixedSize(400, 150)

        # UIの作成
        self._create_widgets(message)

        # 中央に配置
        self.center_on_parent()

    def _create_widgets(self, message: str) -> None:
        """ウィジェットを作成"""
        # メインレイアウト
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # メッセージラベル
        self.message_label = QLabel(message)
        message_font = QFont()
        message_font.setPointSize(10)
        self.message_label.setFont(message_font)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message_label)

        # 不定プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不定モード
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMinimumWidth(300)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def set_message(self, message: str) -> None:
        """
        メッセージを更新

        Args:
            message: 表示するメッセージ
        """
        self.message_label.setText(message)
        self.repaint()

    def closeEvent(self, event) -> None:
        """ウィンドウを閉じようとした時の処理"""
        # 不定進捗ダイアログは閉じるボタンを無効化
        event.ignore()
