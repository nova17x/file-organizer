#!/usr/bin/env python3
"""
PyQt6入力ダイアログのテストスクリプト
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt6.QtCore import Qt

from gui.qt_input_dialogs import CategoryDialog, PatternDialog
from gui.themes import ThemeManager, ThemeType


class TestWindow(QMainWindow):
    """テスト用メインウィンドウ"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Input Dialogs Test")
        self.setGeometry(100, 100, 400, 250)

        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # レイアウト
        layout = QVBoxLayout()

        # テストボタン1: CategoryDialog (新規追加)
        btn1 = QPushButton("Category Dialog をテスト (新規)")
        btn1.clicked.connect(self.test_category_dialog_new)
        layout.addWidget(btn1)

        # テストボタン2: CategoryDialog (編集)
        btn2 = QPushButton("Category Dialog をテスト (編集)")
        btn2.clicked.connect(self.test_category_dialog_edit)
        layout.addWidget(btn2)

        # テストボタン3: PatternDialog (新規追加)
        btn3 = QPushButton("Pattern Dialog をテスト (新規)")
        btn3.clicked.connect(self.test_pattern_dialog_new)
        layout.addWidget(btn3)

        # テストボタン4: PatternDialog (編集)
        btn4 = QPushButton("Pattern Dialog をテスト (編集)")
        btn4.clicked.connect(self.test_pattern_dialog_edit)
        layout.addWidget(btn4)

        # テストボタン5: テーマ切り替え
        btn5 = QPushButton("テーマを切り替え (Dark ⇄ Light)")
        btn5.clicked.connect(self.toggle_theme)
        layout.addWidget(btn5)

        central_widget.setLayout(layout)

        # 現在のテーマ
        self.current_theme = ThemeType.DARK

    def test_category_dialog_new(self):
        """カテゴリダイアログをテスト（新規）"""
        dialog = CategoryDialog(
            parent=self,
            title="カテゴリの追加"
        )

        if dialog.exec_centered():
            if dialog.result:
                category, extensions = dialog.result
                QMessageBox.information(
                    self,
                    "結果",
                    f"カテゴリ: {category}\n拡張子: {', '.join(extensions)}"
                )

    def test_category_dialog_edit(self):
        """カテゴリダイアログをテスト（編集）"""
        dialog = CategoryDialog(
            parent=self,
            title="カテゴリの編集",
            category="画像ファイル",
            extensions=[".jpg", ".png", ".gif"]
        )

        if dialog.exec_centered():
            if dialog.result:
                category, extensions = dialog.result
                QMessageBox.information(
                    self,
                    "結果",
                    f"カテゴリ: {category}\n拡張子: {', '.join(extensions)}"
                )

    def test_pattern_dialog_new(self):
        """パターンダイアログをテスト（新規）"""
        dialog = PatternDialog(
            parent=self,
            title="パターンの追加"
        )

        if dialog.exec_centered():
            if dialog.result:
                category, pattern = dialog.result
                QMessageBox.information(
                    self,
                    "結果",
                    f"カテゴリ: {category}\nパターン: {pattern}"
                )

    def test_pattern_dialog_edit(self):
        """パターンダイアログをテスト（編集）"""
        dialog = PatternDialog(
            parent=self,
            title="パターンの編集",
            category="スクリーンショット",
            pattern="^screenshot[_-].*"
        )

        if dialog.exec_centered():
            if dialog.result:
                category, pattern = dialog.result
                QMessageBox.information(
                    self,
                    "結果",
                    f"カテゴリ: {category}\nパターン: {pattern}"
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
