"""
プレビューダイアログ (PyQt6版)
整理前のアクションをプレビュー表示
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QWidget, QGroupBox, QHeaderView
)
from PyQt6.QtCore import Qt
from typing import List, Dict, Optional, Any
import os

from .base_window import BaseDialog


class PreviewDialog(BaseDialog):
    """整理アクションのプレビューダイアログ"""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        actions: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Args:
            parent: 親ウィジェット
            actions: プレビューするアクションのリスト
        """
        super().__init__(parent, modal=True)

        self.actions = actions or []
        self.filtered_actions = self.actions.copy()
        self.confirmed = False
        self.selected_actions = []

        # ウィンドウの設定
        self.setWindowTitle("プレビュー - 整理内容の確認")
        self.resize(900, 600)

        # UIの作成
        self._create_widgets()

        # データの表示
        self._populate_table()

        # 統計情報の更新
        self._update_statistics()

        # 中央に配置
        self.center_on_parent()

    def _create_widgets(self) -> None:
        """ウィジェットを作成"""
        # メインレイアウト
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 上部: タイトルと統計情報
        top_layout = QHBoxLayout()

        title_label = QLabel("以下のファイルが整理されます")
        title_font = title_label.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        self.stats_label = QLabel("")
        stats_font = self.stats_label.font()
        stats_font.setPointSize(9)
        self.stats_label.setFont(stats_font)
        top_layout.addWidget(self.stats_label)

        layout.addLayout(top_layout)

        # フィルターグループ
        filter_group = QGroupBox("フィルター")
        filter_layout = QHBoxLayout()

        # 検索フィルター
        filter_layout.addWidget(QLabel("検索:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("ファイル名、パスで検索...")
        self.search_edit.setMaximumWidth(300)
        self.search_edit.textChanged.connect(self._apply_filter)
        filter_layout.addWidget(self.search_edit)

        filter_layout.addSpacing(20)

        # タイプフィルター
        filter_layout.addWidget(QLabel("タイプ:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["全て", "move", "copy"])
        self.type_combo.setMaximumWidth(100)
        self.type_combo.currentTextChanged.connect(self._apply_filter)
        filter_layout.addWidget(self.type_combo)

        filter_layout.addStretch()

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # テーブルウィジェット
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            '#', 'タイプ', 'ファイル名', '移動元', '移動先', 'サイズ'
        ])

        # 列幅の設定
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)

        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 60)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(5, 100)

        # テーブル設定
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

        # 下部: ボタン
        button_layout = QHBoxLayout()

        # 選択関連ボタン（左側）
        select_all_button = QPushButton("全て選択")
        select_all_button.clicked.connect(self._select_all)
        button_layout.addWidget(select_all_button)

        deselect_all_button = QPushButton("全て解除")
        deselect_all_button.clicked.connect(self._deselect_all)
        button_layout.addWidget(deselect_all_button)

        button_layout.addStretch()

        # 実行/キャンセルボタン（右側）
        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(self._on_cancel)
        cancel_button.setMinimumWidth(100)
        button_layout.addWidget(cancel_button)

        execute_button = QPushButton("実行")
        execute_button.setObjectName("accentButton")
        execute_button.clicked.connect(self._on_confirm)
        execute_button.setMinimumWidth(100)
        button_layout.addWidget(execute_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _populate_table(self) -> None:
        """テーブルにデータを表示"""
        # 既存の行をクリア
        self.table.setRowCount(0)

        # アクションを追加
        for i, action in enumerate(self.filtered_actions):
            row = self.table.rowCount()
            self.table.insertRow(row)

            filename = action.get('filename', os.path.basename(action['source']))
            size_formatted = self._format_size(action.get('size', 0))

            # 各列のデータを設定
            items = [
                QTableWidgetItem(str(i + 1)),
                QTableWidgetItem(action['type']),
                QTableWidgetItem(filename),
                QTableWidgetItem(action['source']),
                QTableWidgetItem(action['destination']),
                QTableWidgetItem(size_formatted)
            ]

            # アライメント設定
            items[0].setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            items[1].setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            items[5].setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            for col, item in enumerate(items):
                self.table.setItem(row, col, item)

    def _apply_filter(self) -> None:
        """フィルターを適用"""
        search_text = self.search_edit.text().lower()
        action_type = self.type_combo.currentText()

        # フィルタリング
        self.filtered_actions = []

        for action in self.actions:
            # タイプフィルター
            if action_type != "全て" and action['type'] != action_type:
                continue

            # 検索フィルター
            if search_text:
                filename = action.get('filename', os.path.basename(action['source']))
                source = action['source']
                destination = action['destination']

                if not (search_text in filename.lower() or
                       search_text in source.lower() or
                       search_text in destination.lower()):
                    continue

            self.filtered_actions.append(action)

        # テーブルを更新
        self._populate_table()
        self._update_statistics()

    def _update_statistics(self) -> None:
        """統計情報を更新"""
        total = len(self.filtered_actions)
        total_size = sum(action.get('size', 0) for action in self.filtered_actions)

        stats_text = f"表示中: {total}件 / 合計: {len(self.actions)}件 | サイズ: {self._format_size(total_size)}"
        self.stats_label.setText(stats_text)

    def _select_all(self) -> None:
        """すべてのアイテムを選択"""
        self.table.selectAll()

    def _deselect_all(self) -> None:
        """すべての選択を解除"""
        self.table.clearSelection()

    def _on_confirm(self) -> None:
        """実行ボタンが押された時の処理"""
        # 選択されたアイテムを取得
        selected_rows = set(item.row() for item in self.table.selectedItems())

        if not selected_rows:
            # 何も選択されていない場合は全て実行
            self.selected_actions = self.filtered_actions
        else:
            # 選択されたアイテムのみ実行
            self.selected_actions = []
            for row in sorted(selected_rows):
                if 0 <= row < len(self.filtered_actions):
                    self.selected_actions.append(self.filtered_actions[row])

        self.confirmed = True
        self.accept()

    def _on_cancel(self) -> None:
        """キャンセルボタンが押された時の処理"""
        self.confirmed = False
        self.reject()

    def get_confirmed_actions(self) -> Optional[List[Dict[str, Any]]]:
        """
        確認されたアクションのリストを取得

        Returns:
            確認された場合はアクションリスト、キャンセルされた場合はNone
        """
        if self.confirmed:
            return self.selected_actions
        return None

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """
        バイト数を人間が読みやすい形式に変換
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

