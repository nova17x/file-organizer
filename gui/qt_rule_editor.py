"""
ルール編集ダイアログ (PyQt6版)
整理ルールをGUIで作成・編集
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QTabWidget, QWidget,
    QListWidget, QCheckBox, QRadioButton, QComboBox, QMessageBox,
    QFileDialog, QGroupBox, QButtonGroup
)
from PyQt6.QtCore import Qt
from typing import Dict, Optional, List
import json

from .base_window import BaseDialog
from .qt_input_dialogs import CategoryDialog, PatternDialog


class RuleEditorDialog(BaseDialog):
    """ルールを編集するダイアログ"""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        existing_rules: Optional[Dict] = None
    ):
        """
        Args:
            parent: 親ウィジェット
            existing_rules: 既存のルール（編集時）
        """
        super().__init__(parent, modal=True)

        self.existing_rules = existing_rules
        self.result_rules = None

        # ウィンドウの設定
        self.setWindowTitle("ルール編集")
        self.setFixedSize(700, 750)

        # UIの作成
        self._create_widgets()

        # 既存のルールがあれば読み込み
        if existing_rules:
            self._load_existing_rules()

        # 中央に配置
        self.center_on_parent()

    def _create_widgets(self) -> None:
        """ウィジェットを作成"""
        # メインレイアウト
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 上部: 基本情報
        info_group = QGroupBox("基本情報")
        info_layout = QGridLayout()

        # ルール名
        info_layout.addWidget(QLabel("ルール名:"), 0, 0)
        self.name_edit = QLineEdit("新規ルール")
        info_layout.addWidget(self.name_edit, 0, 1)

        # 説明
        info_layout.addWidget(QLabel("説明:"), 1, 0)
        self.desc_edit = QLineEdit()
        info_layout.addWidget(self.desc_edit, 1, 1)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # タブウィジェット
        self.tab_widget = QTabWidget()

        # 各ルールタイプのタブを作成
        self._create_extension_tab()
        self._create_date_tab()
        self._create_size_tab()
        self._create_pattern_tab()

        layout.addWidget(self.tab_widget)

        # 下部: ボタン
        button_layout = QHBoxLayout()

        load_template_button = QPushButton("テンプレート読み込み")
        load_template_button.clicked.connect(self._load_template)
        button_layout.addWidget(load_template_button)

        button_layout.addStretch()

        save_button = QPushButton("保存")
        save_button.clicked.connect(self._on_save)
        save_button.setMinimumWidth(100)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(self._on_cancel)
        cancel_button.setMinimumWidth(100)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _create_extension_tab(self) -> None:
        """拡張子別分類タブを作成"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 有効/無効
        self.ext_enabled = QCheckBox("拡張子による分類を有効にする")
        self.ext_enabled.setChecked(True)
        layout.addWidget(self.ext_enabled)

        # カテゴリリスト
        self.ext_listbox = QListWidget()
        self.ext_listbox.setMinimumHeight(400)
        layout.addWidget(self.ext_listbox)

        # ボタン
        button_layout = QHBoxLayout()
        add_button = QPushButton("追加")
        add_button.clicked.connect(self._add_extension_category)
        button_layout.addWidget(add_button)

        edit_button = QPushButton("編集")
        edit_button.clicked.connect(self._edit_extension_category)
        button_layout.addWidget(edit_button)

        delete_button = QPushButton("削除")
        delete_button.clicked.connect(self._delete_extension_category)
        button_layout.addWidget(delete_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "拡張子分類")

        # デフォルトカテゴリ
        self.ext_categories = {}
        self._load_default_categories()

    def _create_date_tab(self) -> None:
        """日付別分類タブを作成"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 有効/無効
        self.date_enabled = QCheckBox("日付による分類を有効にする")
        self.date_enabled.setChecked(True)
        layout.addWidget(self.date_enabled)

        # 設定グループ
        settings_group = QGroupBox("設定")
        settings_layout = QGridLayout()

        # モード選択
        settings_layout.addWidget(QLabel("基準日付:"), 0, 0)

        mode_layout = QHBoxLayout()
        self.date_mode_group = QButtonGroup()
        self.date_modified_radio = QRadioButton("更新日")
        self.date_modified_radio.setChecked(True)
        self.date_created_radio = QRadioButton("作成日")

        self.date_mode_group.addButton(self.date_modified_radio, 0)
        self.date_mode_group.addButton(self.date_created_radio, 1)

        mode_layout.addWidget(self.date_modified_radio)
        mode_layout.addWidget(self.date_created_radio)
        mode_layout.addStretch()

        mode_widget = QWidget()
        mode_widget.setLayout(mode_layout)
        settings_layout.addWidget(mode_widget, 0, 1)

        # フォーマット選択
        settings_layout.addWidget(QLabel("フォルダ形式:"), 1, 0)
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems([
            "%Y/%m",
            "%Y/%m/%d",
            "%Y",
            "%Y-%m",
            "%Y-%m-%d"
        ])
        settings_layout.addWidget(self.date_format_combo, 1, 1, Qt.AlignmentFlag.AlignLeft)

        # 例の表示
        example_label = QLabel("例: 2026/01 (年/月)")
        example_label.setStyleSheet("color: gray; font-style: italic;")
        settings_layout.addWidget(example_label, 2, 1)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        layout.addStretch()

        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "日付分類")

    def _create_size_tab(self) -> None:
        """サイズ別分類タブを作成"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 有効/無効
        self.size_enabled = QCheckBox("サイズによる分類を有効にする")
        self.size_enabled.setChecked(False)
        layout.addWidget(self.size_enabled)

        # 閾値設定
        settings_group = QGroupBox("サイズ閾値")
        settings_layout = QGridLayout()

        # Small
        settings_layout.addWidget(QLabel("Small (小):"), 0, 0)
        small_layout = QHBoxLayout()
        self.size_small_edit = QLineEdit("1")
        self.size_small_edit.setMaximumWidth(100)
        small_layout.addWidget(self.size_small_edit)
        small_layout.addWidget(QLabel("MB 以下"))
        small_layout.addStretch()
        small_widget = QWidget()
        small_widget.setLayout(small_layout)
        settings_layout.addWidget(small_widget, 0, 1)

        # Medium
        settings_layout.addWidget(QLabel("Medium (中):"), 1, 0)
        medium_layout = QHBoxLayout()
        self.size_medium_edit = QLineEdit("100")
        self.size_medium_edit.setMaximumWidth(100)
        medium_layout.addWidget(self.size_medium_edit)
        medium_layout.addWidget(QLabel("MB 以下"))
        medium_layout.addStretch()
        medium_widget = QWidget()
        medium_widget.setLayout(medium_layout)
        settings_layout.addWidget(medium_widget, 1, 1)

        # Large
        settings_layout.addWidget(QLabel("Large (大):"), 2, 0)
        large_layout = QHBoxLayout()
        self.size_large_edit = QLineEdit("1024")
        self.size_large_edit.setMaximumWidth(100)
        large_layout.addWidget(self.size_large_edit)
        large_layout.addWidget(QLabel("MB 以下"))
        large_layout.addStretch()
        large_widget = QWidget()
        large_widget.setLayout(large_layout)
        settings_layout.addWidget(large_widget, 2, 1)

        # 注意書き
        note_label = QLabel("※ これらを超えるものはVeryLarge（特大）に分類されます")
        note_label.setStyleSheet("color: gray; font-size: 10px;")
        settings_layout.addWidget(note_label, 3, 1)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        layout.addStretch()

        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "サイズ分類")

    def _create_pattern_tab(self) -> None:
        """パターン分類タブを作成"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 有効/無効
        self.pattern_enabled = QCheckBox("ファイル名パターンによる分類を有効にする")
        self.pattern_enabled.setChecked(True)
        layout.addWidget(self.pattern_enabled)

        # パターンリスト
        self.pattern_listbox = QListWidget()
        self.pattern_listbox.setMinimumHeight(400)
        layout.addWidget(self.pattern_listbox)

        # ボタン
        button_layout = QHBoxLayout()
        add_button = QPushButton("追加")
        add_button.clicked.connect(self._add_pattern)
        button_layout.addWidget(add_button)

        edit_button = QPushButton("編集")
        edit_button.clicked.connect(self._edit_pattern)
        button_layout.addWidget(edit_button)

        delete_button = QPushButton("削除")
        delete_button.clicked.connect(self._delete_pattern)
        button_layout.addWidget(delete_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "パターン分類")

        # デフォルトパターン
        self.patterns = {}
        self._load_default_patterns()

    def _load_default_categories(self) -> None:
        """デフォルトカテゴリを読み込み"""
        default_categories = {
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
            "Videos": [".mp4", ".avi", ".mkv", ".mov"],
            "Documents": [".pdf", ".doc", ".docx", ".txt"],
            "Audio": [".mp3", ".wav", ".flac", ".aac"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"]
        }

        for category, extensions in default_categories.items():
            self.ext_categories[category] = extensions
            self.ext_listbox.addItem(f"{category}: {', '.join(extensions)}")

    def _load_default_patterns(self) -> None:
        """デフォルトパターンを読み込み"""
        default_patterns = {
            "Screenshots": "^screenshot[_-].*",
            "Camera": "^(IMG|DSC|DCIM)[_-].*"
        }

        for category, pattern in default_patterns.items():
            self.patterns[category] = pattern
            self.pattern_listbox.addItem(f"{category}: {pattern}")

    def _add_extension_category(self) -> None:
        """拡張子カテゴリを追加"""
        dialog = CategoryDialog(self, "拡張子カテゴリの追加")

        if dialog.exec():
            if dialog.result:
                category, extensions = dialog.result
                self.ext_categories[category] = extensions
                self.ext_listbox.addItem(f"{category}: {', '.join(extensions)}")

    def _edit_extension_category(self) -> None:
        """拡張子カテゴリを編集"""
        current_item = self.ext_listbox.currentRow()
        if current_item < 0:
            QMessageBox.warning(self, "警告", "編集するカテゴリを選択してください")
            return

        category_name = list(self.ext_categories.keys())[current_item]
        extensions = self.ext_categories[category_name]

        dialog = CategoryDialog(
            self,
            "拡張子カテゴリの編集",
            category_name,
            extensions
        )

        if dialog.exec():
            if dialog.result:
                new_category, new_extensions = dialog.result
                del self.ext_categories[category_name]
                self.ext_categories[new_category] = new_extensions
                self.ext_listbox.item(current_item).setText(
                    f"{new_category}: {', '.join(new_extensions)}"
                )

    def _delete_extension_category(self) -> None:
        """拡張子カテゴリを削除"""
        current_item = self.ext_listbox.currentRow()
        if current_item < 0:
            QMessageBox.warning(self, "警告", "削除するカテゴリを選択してください")
            return

        category_name = list(self.ext_categories.keys())[current_item]
        del self.ext_categories[category_name]
        self.ext_listbox.takeItem(current_item)

    def _add_pattern(self) -> None:
        """パターンを追加"""
        dialog = PatternDialog(self, "パターンの追加")

        if dialog.exec():
            if dialog.result:
                category, pattern = dialog.result
                self.patterns[category] = pattern
                self.pattern_listbox.addItem(f"{category}: {pattern}")

    def _edit_pattern(self) -> None:
        """パターンを編集"""
        current_item = self.pattern_listbox.currentRow()
        if current_item < 0:
            QMessageBox.warning(self, "警告", "編集するパターンを選択してください")
            return

        category_name = list(self.patterns.keys())[current_item]
        pattern = self.patterns[category_name]

        dialog = PatternDialog(
            self,
            "パターンの編集",
            category_name,
            pattern
        )

        if dialog.exec():
            if dialog.result:
                new_category, new_pattern = dialog.result
                del self.patterns[category_name]
                self.patterns[new_category] = new_pattern
                self.pattern_listbox.item(current_item).setText(
                    f"{new_category}: {new_pattern}"
                )

    def _delete_pattern(self) -> None:
        """パターンを削除"""
        current_item = self.pattern_listbox.currentRow()
        if current_item < 0:
            QMessageBox.warning(self, "警告", "削除するパターンを選択してください")
            return

        category_name = list(self.patterns.keys())[current_item]
        del self.patterns[category_name]
        self.pattern_listbox.takeItem(current_item)

    def _load_template(self) -> None:
        """テンプレートを読み込み"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "テンプレートを開く",
            "",
            "JSONファイル (*.json);;すべてのファイル (*.*)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    rules = json.load(f)
                self._load_existing_rules(rules)
                QMessageBox.information(self, "成功", "テンプレートを読み込みました")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"テンプレートの読み込みに失敗しました:\n{e}")

    def _load_existing_rules(self, rules: Optional[Dict] = None) -> None:
        """既存のルールを読み込み"""
        if rules is None:
            rules = self.existing_rules

        if not rules:
            return

        # 基本情報
        self.name_edit.setText(rules.get("name", ""))
        self.desc_edit.setText(rules.get("description", ""))

        # 各ルールを読み込み
        for rule in rules.get("rules", []):
            rule_type = rule.get("type")

            if rule_type == "extension" and "categories" in rule:
                self.ext_enabled.setChecked(rule.get("enabled", True))
                self.ext_categories = rule["categories"]
                self.ext_listbox.clear()
                for category, extensions in self.ext_categories.items():
                    self.ext_listbox.addItem(f"{category}: {', '.join(extensions)}")

            elif rule_type == "date":
                self.date_enabled.setChecked(rule.get("enabled", True))
                mode = rule.get("mode", "modified")
                if mode == "modified":
                    self.date_modified_radio.setChecked(True)
                else:
                    self.date_created_radio.setChecked(True)

                date_format = rule.get("format", "%Y/%m")
                index = self.date_format_combo.findText(date_format)
                if index >= 0:
                    self.date_format_combo.setCurrentIndex(index)

            elif rule_type == "size" and "thresholds" in rule:
                self.size_enabled.setChecked(rule.get("enabled", True))
                thresholds = rule["thresholds"]
                if "Small" in thresholds:
                    self.size_small_edit.setText(str(thresholds["Small"] // (1024 * 1024)))
                if "Medium" in thresholds:
                    self.size_medium_edit.setText(str(thresholds["Medium"] // (1024 * 1024)))
                if "Large" in thresholds:
                    self.size_large_edit.setText(str(thresholds["Large"] // (1024 * 1024)))

            elif rule_type == "pattern" and "patterns" in rule:
                self.pattern_enabled.setChecked(rule.get("enabled", True))
                self.patterns = rule["patterns"]
                self.pattern_listbox.clear()
                for category, pattern in self.patterns.items():
                    self.pattern_listbox.addItem(f"{category}: {pattern}")

    def _on_save(self) -> None:
        """保存ボタンが押された時の処理"""
        # ルールを構築
        rules = {
            "name": self.name_edit.text() or "新規ルール",
            "version": "1.0",
            "description": self.desc_edit.text(),
            "priority": ["pattern", "extension", "date", "size"],
            "rules": []
        }

        # 拡張子ルール
        if self.ext_enabled.isChecked() and self.ext_categories:
            rules["rules"].append({
                "type": "extension",
                "enabled": True,
                "categories": self.ext_categories
            })

        # 日付ルール
        if self.date_enabled.isChecked():
            mode = "modified" if self.date_modified_radio.isChecked() else "created"
            rules["rules"].append({
                "type": "date",
                "enabled": True,
                "mode": mode,
                "format": self.date_format_combo.currentText()
            })

        # サイズルール
        if self.size_enabled.isChecked():
            try:
                rules["rules"].append({
                    "type": "size",
                    "enabled": True,
                    "thresholds": {
                        "Small": int(float(self.size_small_edit.text()) * 1024 * 1024),
                        "Medium": int(float(self.size_medium_edit.text()) * 1024 * 1024),
                        "Large": int(float(self.size_large_edit.text()) * 1024 * 1024)
                    }
                })
            except ValueError:
                QMessageBox.critical(self, "エラー", "サイズの値が不正です")
                return

        # パターンルール
        if self.pattern_enabled.isChecked() and self.patterns:
            rules["rules"].append({
                "type": "pattern",
                "enabled": True,
                "patterns": self.patterns
            })

        self.result_rules = rules
        self.accept()

    def _on_cancel(self) -> None:
        """キャンセルボタンが押された時の処理"""
        self.result_rules = None
        self.reject()

