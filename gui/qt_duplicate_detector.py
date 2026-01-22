"""
重複ファイル検出ダイアログ (PyQt6版)
重複ファイルの検出と管理
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLabel, QLineEdit, QFileDialog, QCheckBox, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from typing import Optional, List, Dict
import os

from .base_window import BaseDialog
from .qt_progress_dialog import IndeterminateProgressDialog


class DuplicateDetectorWorker(QThread):
    """重複検出ワーカー"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, detector, directory):
        super().__init__()
        self.detector = detector
        self.directory = directory

    def run(self):
        try:
            duplicates = self.detector.find_duplicates(self.directory)
            self.finished.emit(duplicates)
        except Exception as e:
            self.error.emit(str(e))


class DuplicateDetectorDialog(BaseDialog):
    """重複ファイル検出ダイアログ"""

    def __init__(self, parent=None, duplicate_detector=None):
        """
        Args:
            parent: 親ウィジェット
            duplicate_detector: DuplicateDetector インスタンス
        """
        super().__init__(parent, modal=True)

        self.duplicate_detector = duplicate_detector
        self.duplicates = {}
        self.current_worker = None
        self.current_progress_dialog = None

        self.setWindowTitle("重複ファイル検出")
        self.setMinimumSize(900, 600)

        self._create_widgets()

        self.center_on_parent()

    def _create_widgets(self) -> None:
        """ウィジェットを作成"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 検索設定
        search_group = QGroupBox("検索設定")
        search_layout = QVBoxLayout()

        # ディレクトリ選択
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("検索ディレクトリ:"))
        self.dir_edit = QLineEdit()
        dir_layout.addWidget(self.dir_edit)
        browse_btn = QPushButton("参照")
        browse_btn.clicked.connect(self._browse_directory)
        dir_layout.addWidget(browse_btn)
        search_layout.addLayout(dir_layout)

        # オプション
        options_layout = QHBoxLayout()
        self.recursive_check = QCheckBox("サブディレクトリも検索")
        self.recursive_check.setChecked(True)
        options_layout.addWidget(self.recursive_check)

        self.show_details_check = QCheckBox("詳細を表示")
        self.show_details_check.setChecked(True)
        options_layout.addWidget(self.show_details_check)

        options_layout.addStretch()
        search_layout.addLayout(options_layout)

        # 検索ボタン
        search_btn = QPushButton("検索開始")
        search_btn.clicked.connect(self._start_detection)
        search_btn.setMinimumHeight(35)
        search_layout.addWidget(search_btn)

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # 結果表示
        result_label = QLabel("重複ファイル一覧:")
        layout.addWidget(result_label)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels([
            "ファイル名", "サイズ", "重複数", "パス", "ハッシュ"
        ])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.result_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.result_table)

        # ボタン
        button_layout = QHBoxLayout()

        delete_btn = QPushButton("選択したファイルを削除")
        delete_btn.clicked.connect(self._delete_selected)
        button_layout.addWidget(delete_btn)

        button_layout.addStretch()

        close_btn = QPushButton("閉じる")
        close_btn.clicked.connect(self.accept)
        close_btn.setMinimumWidth(100)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _browse_directory(self) -> None:
        """ディレクトリを選択"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "検索ディレクトリを選択"
        )
        if directory:
            self.dir_edit.setText(directory)

    def _start_detection(self) -> None:
        """重複検出を開始"""
        directory = self.dir_edit.text()

        if not directory:
            QMessageBox.critical(self, "エラー", "検索ディレクトリを選択してください")
            return

        if not os.path.exists(directory):
            QMessageBox.critical(self, "エラー", "指定されたディレクトリが存在しません")
            return

        # 進捗ダイアログを表示
        self.current_progress_dialog = IndeterminateProgressDialog(
            self,
            title="重複検出中",
            message="ファイルをスキャンしています..."
        )
        self.current_progress_dialog.show()

        # ワーカーで実行
        self.current_worker = DuplicateDetectorWorker(
            self.duplicate_detector,
            directory
        )

        self.current_worker.finished.connect(self._on_detection_finished)
        self.current_worker.error.connect(self._on_detection_error)

        self.current_worker.start()

    def _on_detection_finished(self, duplicates: Dict) -> None:
        """検出完了時の処理"""
        if self.current_progress_dialog:
            self.current_progress_dialog.close()
            self.current_progress_dialog.deleteLater()
            self.current_progress_dialog = None

        self.duplicates = duplicates
        self._display_results()

    def _on_detection_error(self, error: str) -> None:
        """検出エラー時の処理"""
        if self.current_progress_dialog:
            self.current_progress_dialog.close()
            self.current_progress_dialog.deleteLater()
            self.current_progress_dialog = None

        QMessageBox.critical(self, "エラー", f"重複検出中にエラーが発生しました:\n{error}")

    def _display_results(self) -> None:
        """検出結果を表示"""
        self.result_table.setRowCount(0)

        if not self.duplicates:
            QMessageBox.information(self, "結果", "重複ファイルは見つかりませんでした")
            return

        total_duplicates = 0
        total_wasted_space = 0

        for file_hash, file_list in self.duplicates.items():
            if len(file_list) < 2:
                continue

            # 最初のファイルを基準とする
            first_file = file_list[0]
            file_size = first_file.get("size", 0)
            duplicate_count = len(file_list)
            wasted_space = file_size * (duplicate_count - 1)

            total_duplicates += duplicate_count - 1
            total_wasted_space += wasted_space

            # 各重複ファイルを追加
            for file_info in file_list:
                row = self.result_table.rowCount()
                self.result_table.insertRow(row)

                # ファイル名
                filename = os.path.basename(file_info.get("path", ""))
                self.result_table.setItem(row, 0, QTableWidgetItem(filename))

                # サイズ
                size_formatted = self._format_size(file_info.get("size", 0))
                self.result_table.setItem(row, 1, QTableWidgetItem(size_formatted))

                # 重複数
                self.result_table.setItem(row, 2, QTableWidgetItem(str(duplicate_count)))

                # パス
                self.result_table.setItem(row, 3, QTableWidgetItem(file_info.get("path", "")))

                # ハッシュ（詳細表示時のみ）
                if self.show_details_check.isChecked():
                    self.result_table.setItem(row, 4, QTableWidgetItem(file_hash[:16] + "..."))
                else:
                    self.result_table.setItem(row, 4, QTableWidgetItem(""))

        # 結果メッセージ
        wasted_formatted = self._format_size(total_wasted_space)
        QMessageBox.information(
            self,
            "検出完了",
            f"重複ファイルを検出しました\n\n"
            f"重複ファイル数: {total_duplicates}件\n"
            f"無駄な容量: {wasted_formatted}"
        )

    def _delete_selected(self) -> None:
        """選択されたファイルを削除"""
        selected_rows = self.result_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "削除するファイルを選択してください")
            return

        # 選択された行を取得
        rows_to_delete = set()
        for index in selected_rows:
            rows_to_delete.add(index.row())

        files_to_delete = []
        for row in sorted(rows_to_delete):
            path_item = self.result_table.item(row, 3)
            if path_item:
                files_to_delete.append(path_item.text())

        # 確認
        reply = QMessageBox.question(
            self,
            "確認",
            f"{len(files_to_delete)}件のファイルを削除しますか？\n\n"
            f"注意: この操作は取り消せません。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 削除
        deleted_count = 0
        failed_count = 0

        for file_path in files_to_delete:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_count += 1
            except Exception as e:
                failed_count += 1
                print(f"エラー: {file_path} の削除に失敗: {e}")

        # 結果表示
        QMessageBox.information(
            self,
            "完了",
            f"削除完了\n\n成功: {deleted_count}件\n失敗: {failed_count}件"
        )

        # 再検索
        if deleted_count > 0:
            self._start_detection()

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """バイト数を人間が読みやすい形式に変換"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
