#!/usr/bin/env python3
"""
PyQt6プレビューダイアログのテストスクリプト
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt6.QtCore import Qt

from gui.qt_preview_dialog import PreviewDialog
from gui.themes import ThemeManager, ThemeType


class TestWindow(QMainWindow):
    """テスト用メインウィンドウ"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Preview Dialog Test")
        self.setGeometry(100, 100, 400, 200)

        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # レイアウト
        layout = QVBoxLayout()

        # テストボタン1: 小規模データ
        btn1 = QPushButton("プレビューをテスト (10ファイル)")
        btn1.clicked.connect(self.test_small_preview)
        layout.addWidget(btn1)

        # テストボタン2: 中規模データ
        btn2 = QPushButton("プレビューをテスト (100ファイル)")
        btn2.clicked.connect(self.test_large_preview)
        layout.addWidget(btn2)

        # テストボタン3: テーマ切り替え
        btn3 = QPushButton("テーマを切り替え (Dark ⇄ Light)")
        btn3.clicked.connect(self.toggle_theme)
        layout.addWidget(btn3)

        central_widget.setLayout(layout)

        # 現在のテーマ
        self.current_theme = ThemeType.DARK

    def test_small_preview(self):
        """小規模データでプレビューをテスト"""
        actions = self._create_sample_actions(10)
        self._show_preview(actions)

    def test_large_preview(self):
        """大規模データでプレビューをテスト"""
        actions = self._create_sample_actions(100)
        self._show_preview(actions)

    def _show_preview(self, actions):
        """プレビューダイアログを表示"""
        dialog = PreviewDialog(self, actions)

        if dialog.exec_centered():
            confirmed_actions = dialog.get_confirmed_actions()
            if confirmed_actions:
                QMessageBox.information(
                    self,
                    "確認",
                    f"{len(confirmed_actions)}件のファイルを整理することが確認されました"
                )
        else:
            QMessageBox.information(self, "キャンセル", "整理がキャンセルされました")

    def _create_sample_actions(self, count):
        """サンプルアクションを生成"""
        actions = []
        types = ["move", "copy"]
        file_types = [
            (".jpg", "Images", 1024 * 1024 * 2),
            (".mp4", "Videos", 1024 * 1024 * 50),
            (".pdf", "Documents", 1024 * 500),
            (".txt", "Documents", 1024 * 10),
            (".mp3", "Audio", 1024 * 1024 * 5)
        ]

        for i in range(count):
            ext, category, size_base = file_types[i % len(file_types)]
            action_type = types[i % len(types)]

            actions.append({
                "type": action_type,
                "filename": f"sample_file_{i+1}{ext}",
                "source": f"/home/user/Downloads/sample_file_{i+1}{ext}",
                "destination": f"/home/user/Organized/{category}/sample_file_{i+1}{ext}",
                "size": size_base + (i * 1024)
            })

        return actions

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
