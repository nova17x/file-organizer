#!/usr/bin/env python3
"""
PyQt6ルールエディタのテストスクリプト
"""

import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox, QTextEdit
from PyQt6.QtCore import Qt

from gui.qt_rule_editor import RuleEditorDialog
from gui.themes import ThemeManager, ThemeType


class TestWindow(QMainWindow):
    """テスト用メインウィンドウ"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rule Editor Test")
        self.setGeometry(100, 100, 600, 400)

        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # レイアウト
        layout = QVBoxLayout()

        # テストボタン1: 新規ルール作成
        btn1 = QPushButton("新規ルールを作成")
        btn1.clicked.connect(self.test_new_rule)
        layout.addWidget(btn1)

        # テストボタン2: 既存ルール編集
        btn2 = QPushButton("既存ルールを編集")
        btn2.clicked.connect(self.test_edit_rule)
        layout.addWidget(btn2)

        # テストボタン3: テーマ切り替え
        btn3 = QPushButton("テーマを切り替え (Dark ⇄ Light)")
        btn3.clicked.connect(self.toggle_theme)
        layout.addWidget(btn3)

        # 結果表示用テキストエリア
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("ルール作成後、結果がここに表示されます...")
        layout.addWidget(self.result_text)

        central_widget.setLayout(layout)

        # 現在のテーマ
        self.current_theme = ThemeType.DARK

    def test_new_rule(self):
        """新規ルールを作成"""
        dialog = RuleEditorDialog(self)

        if dialog.exec_centered():
            if dialog.result_rules:
                # 結果を表示
                rules_json = json.dumps(dialog.result_rules, indent=2, ensure_ascii=False)
                self.result_text.setPlainText(f"作成されたルール:\n\n{rules_json}")

                # 確認メッセージ
                QMessageBox.information(
                    self,
                    "成功",
                    f"ルール '{dialog.result_rules['name']}' が作成されました"
                )

    def test_edit_rule(self):
        """既存ルールを編集"""
        # サンプルルール
        sample_rule = {
            "name": "サンプル整理ルール",
            "version": "1.0",
            "description": "画像と動画を整理するルール",
            "priority": ["pattern", "extension", "date", "size"],
            "rules": [
                {
                    "type": "extension",
                    "enabled": True,
                    "categories": {
                        "Images": [".jpg", ".png"],
                        "Videos": [".mp4", ".avi"]
                    }
                },
                {
                    "type": "date",
                    "enabled": True,
                    "mode": "modified",
                    "format": "%Y/%m"
                },
                {
                    "type": "size",
                    "enabled": False,
                    "thresholds": {
                        "Small": 1048576,
                        "Medium": 104857600,
                        "Large": 1073741824
                    }
                },
                {
                    "type": "pattern",
                    "enabled": True,
                    "patterns": {
                        "Screenshots": "^screenshot[_-].*"
                    }
                }
            ]
        }

        dialog = RuleEditorDialog(self, sample_rule)

        if dialog.exec_centered():
            if dialog.result_rules:
                # 結果を表示
                rules_json = json.dumps(dialog.result_rules, indent=2, ensure_ascii=False)
                self.result_text.setPlainText(f"編集されたルール:\n\n{rules_json}")

                # 確認メッセージ
                QMessageBox.information(
                    self,
                    "成功",
                    f"ルール '{dialog.result_rules['name']}' が更新されました"
                )

    def toggle_theme(self):
        """テーマを切り替え"""
        if self.current_theme == ThemeType.DARK:
            self.current_theme = ThemeType.LIGHT
        else:
            self.current_theme = ThemeType.DARK

        app = QApplication.instance()
        ThemeManager.apply_theme(app, self.current_theme)


def main():
    app = QApplication(sys.argv)

    # デフォルトテーマを適用
    ThemeManager.apply_theme(app, ThemeType.DARK)

    # テストウィンドウを表示
    window = TestWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
