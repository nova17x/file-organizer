"""
ログビューワダイアログ (PyQt6版)
操作ログの表示と管理
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt
from typing import Optional
import json
import os

from .base_window import BaseDialog


class LogViewerDialog(BaseDialog):
    """ログビューワダイアログ"""

    def __init__(self, parent=None, logger=None):
        """
        Args:
            parent: 親ウィジェット
            logger: OperationLogger インスタンス
        """
        super().__init__(parent, modal=True)

        self.logger = logger
        self.logs = []

        self.setWindowTitle("ログビューワ")
        self.setMinimumSize(900, 600)

        self._create_widgets()
        self._load_logs()

        self.center_on_parent()

    def _create_widgets(self) -> None:
        """ウィジェットを作成"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # スプリッター（上下分割）
        splitter = QSplitter(Qt.Orientation.Vertical)

        # 上部: ログ一覧
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(4)
        self.log_table.setHorizontalHeaderLabels(["日時", "操作名", "アクション数", "ログファイル"])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.log_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.log_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.log_table.itemSelectionChanged.connect(self._on_log_selected)
        splitter.addWidget(self.log_table)

        # 下部: ログ詳細
        self.log_detail = QTextEdit()
        self.log_detail.setReadOnly(True)
        self.log_detail.setMinimumHeight(200)
        splitter.addWidget(self.log_detail)

        # スプリッターの初期サイズ設定
        splitter.setSizes([400, 200])

        layout.addWidget(splitter)

        # ボタン
        button_layout = QHBoxLayout()

        refresh_btn = QPushButton("更新")
        refresh_btn.clicked.connect(self._load_logs)
        button_layout.addWidget(refresh_btn)

        delete_btn = QPushButton("削除")
        delete_btn.clicked.connect(self._delete_log)
        button_layout.addWidget(delete_btn)

        button_layout.addStretch()

        close_btn = QPushButton("閉じる")
        close_btn.clicked.connect(self.accept)
        close_btn.setMinimumWidth(100)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _load_logs(self) -> None:
        """ログを読み込み"""
        if not self.logger:
            return

        self.logs = self.logger.list_logs()
        self.log_table.setRowCount(0)

        for log in self.logs:
            row = self.log_table.rowCount()
            self.log_table.insertRow(row)

            # 日時
            self.log_table.setItem(row, 0, QTableWidgetItem(log.get("timestamp", "不明")))

            # 操作名
            self.log_table.setItem(row, 1, QTableWidgetItem(log.get("operation_name", "不明")))

            # アクション数
            action_count = str(log.get("action_count", 0))
            self.log_table.setItem(row, 2, QTableWidgetItem(action_count))

            # ログファイル
            log_file = os.path.basename(log.get("path", ""))
            self.log_table.setItem(row, 3, QTableWidgetItem(log_file))

    def _on_log_selected(self) -> None:
        """ログが選択された時の処理"""
        selected_rows = self.log_table.selectedIndexes()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        if row >= len(self.logs):
            return

        log = self.logs[row]
        log_path = log.get("path")

        if not log_path or not os.path.exists(log_path):
            self.log_detail.setPlainText("ログファイルが見つかりません")
            return

        # ログファイルを読み込んで表示
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                log_data = json.load(f)

            # 整形して表示
            detail_text = f"操作ID: {log_data.get('operation_id', '不明')}\n"
            detail_text += f"開始時刻: {log_data.get('start_time', '不明')}\n"
            detail_text += f"終了時刻: {log_data.get('end_time', '不明')}\n"
            detail_text += f"操作名: {log_data.get('operation_name', '不明')}\n\n"

            actions = log_data.get('actions', [])
            detail_text += f"アクション数: {len(actions)}\n"
            detail_text += "=" * 80 + "\n\n"

            # 各アクションを表示
            for i, action in enumerate(actions, 1):
                detail_text += f"[{i}] {action.get('type', '不明').upper()}\n"
                detail_text += f"  元: {action.get('source', '不明')}\n"
                detail_text += f"  先: {action.get('destination', '不明')}\n"
                detail_text += f"  状態: {action.get('status', '不明')}\n"

                if 'error' in action:
                    detail_text += f"  エラー: {action['error']}\n"
                if 'reason' in action:
                    detail_text += f"  理由: {action['reason']}\n"

                detail_text += "\n"

            self.log_detail.setPlainText(detail_text)

        except Exception as e:
            self.log_detail.setPlainText(f"ログファイルの読み込みエラー:\n{str(e)}")

    def _delete_log(self) -> None:
        """選択されたログを削除"""
        selected_rows = self.log_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "削除するログを選択してください")
            return

        row = selected_rows[0].row()
        if row >= len(self.logs):
            return

        log = self.logs[row]
        log_path = log.get("path")

        # 確認
        reply = QMessageBox.question(
            self,
            "確認",
            f"以下のログを削除しますか？\n\n{log.get('operation_name', '不明')} ({log.get('timestamp', '不明')})",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 削除
        try:
            if os.path.exists(log_path):
                os.remove(log_path)
                QMessageBox.information(self, "成功", "ログを削除しました")
                self._load_logs()
                self.log_detail.clear()
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"ログの削除に失敗しました:\n{str(e)}")
