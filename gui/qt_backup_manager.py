"""
バックアップ管理ダイアログ (PyQt6版)
バックアップの表示、復元、削除
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLabel
)
from PyQt6.QtCore import Qt
from typing import Optional
import os

from .base_window import BaseDialog


class BackupManagerDialog(BaseDialog):
    """バックアップ管理ダイアログ"""

    def __init__(self, parent=None, backup_manager=None):
        """
        Args:
            parent: 親ウィジェット
            backup_manager: BackupManager インスタンス
        """
        super().__init__(parent, modal=True)

        self.backup_manager = backup_manager
        self.backups = []

        self.setWindowTitle("バックアップ管理")
        self.setMinimumSize(800, 500)

        self._create_widgets()
        self._load_backups()

        self.center_on_parent()

    def _create_widgets(self) -> None:
        """ウィジェットを作成"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 情報ラベル
        info_label = QLabel("バックアップの一覧です。復元または削除を行えます。")
        info_label.setStyleSheet("color: gray;")
        layout.addWidget(info_label)

        # バックアップ一覧テーブル
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(5)
        self.backup_table.setHorizontalHeaderLabels([
            "バックアップID", "作成日時", "ソースディレクトリ", "サイズ", "ファイル数"
        ])
        self.backup_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.backup_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.backup_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.backup_table)

        # ボタン
        button_layout = QHBoxLayout()

        refresh_btn = QPushButton("更新")
        refresh_btn.clicked.connect(self._load_backups)
        button_layout.addWidget(refresh_btn)

        restore_btn = QPushButton("復元")
        restore_btn.clicked.connect(self._restore_backup)
        button_layout.addWidget(restore_btn)

        delete_btn = QPushButton("削除")
        delete_btn.clicked.connect(self._delete_backup)
        button_layout.addWidget(delete_btn)

        button_layout.addStretch()

        close_btn = QPushButton("閉じる")
        close_btn.clicked.connect(self.accept)
        close_btn.setMinimumWidth(100)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _load_backups(self) -> None:
        """バックアップを読み込み"""
        if not self.backup_manager:
            return

        self.backups = self.backup_manager.list_backups()
        self.backup_table.setRowCount(0)

        for backup in self.backups:
            row = self.backup_table.rowCount()
            self.backup_table.insertRow(row)

            # バックアップID
            backup_id = backup.get("backup_id", "不明")
            self.backup_table.setItem(row, 0, QTableWidgetItem(backup_id))

            # 作成日時
            timestamp = backup.get("timestamp", "不明")
            self.backup_table.setItem(row, 1, QTableWidgetItem(timestamp))

            # ソースディレクトリ
            source_dir = backup.get("source_directory", "不明")
            self.backup_table.setItem(row, 2, QTableWidgetItem(source_dir))

            # サイズ
            size = backup.get("total_size_formatted", "不明")
            self.backup_table.setItem(row, 3, QTableWidgetItem(size))

            # ファイル数
            file_count = str(backup.get("file_count", 0))
            self.backup_table.setItem(row, 4, QTableWidgetItem(file_count))

    def _restore_backup(self) -> None:
        """選択されたバックアップを復元"""
        selected_rows = self.backup_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "復元するバックアップを選択してください")
            return

        row = selected_rows[0].row()
        if row >= len(self.backups):
            return

        backup = self.backups[row]
        backup_id = backup.get("backup_id")

        # 確認
        reply = QMessageBox.question(
            self,
            "確認",
            f"以下のバックアップを復元しますか？\n\n"
            f"ID: {backup_id}\n"
            f"作成日時: {backup.get('timestamp', '不明')}\n"
            f"ソース: {backup.get('source_directory', '不明')}\n\n"
            f"注意: 現在のファイルは上書きされます。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 復元
        try:
            success = self.backup_manager.restore_backup(backup_id)
            if success:
                QMessageBox.information(self, "成功", "バックアップを復元しました")
            else:
                QMessageBox.warning(self, "警告", "バックアップの復元に失敗しました")
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"バックアップの復元に失敗しました:\n{str(e)}")

    def _delete_backup(self) -> None:
        """選択されたバックアップを削除"""
        selected_rows = self.backup_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "削除するバックアップを選択してください")
            return

        row = selected_rows[0].row()
        if row >= len(self.backups):
            return

        backup = self.backups[row]
        backup_id = backup.get("backup_id")

        # 確認
        reply = QMessageBox.question(
            self,
            "確認",
            f"以下のバックアップを削除しますか？\n\n"
            f"ID: {backup_id}\n"
            f"作成日時: {backup.get('timestamp', '不明')}\n\n"
            f"注意: この操作は取り消せません。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 削除
        try:
            success = self.backup_manager.delete_backup(backup_id)
            if success:
                QMessageBox.information(self, "成功", "バックアップを削除しました")
                self._load_backups()
            else:
                QMessageBox.warning(self, "警告", "バックアップの削除に失敗しました")
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"バックアップの削除に失敗しました:\n{str(e)}")
