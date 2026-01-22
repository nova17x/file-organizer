#!/usr/bin/env python3
"""
PyQt6プログレスダイアログのテストスクリプト
"""

import sys
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import QThread, pyqtSignal

from gui.qt_progress_dialog import ProgressDialog, IndeterminateProgressDialog
from gui.themes import ThemeManager, ThemeType


class Worker(QThread):
    """プログレスをシミュレートするワーカー"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal()

    def __init__(self, total_items=100):
        super().__init__()
        self.total_items = total_items

    def run(self):
        for i in range(self.total_items + 1):
            time.sleep(0.05)  # 50ms待機
            self.progress.emit(i, f"処理中: アイテム {i}/{self.total_items}")
        self.finished.emit()


class TestWindow(QMainWindow):
    """テスト用メインウィンドウ"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Progress Dialog Test")
        self.setGeometry(100, 100, 400, 200)

        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # レイアウト
        layout = QVBoxLayout()

        # テストボタン1: 確定進捗ダイアログ
        btn1 = QPushButton("Determinate Progress Dialog をテスト")
        btn1.clicked.connect(self.test_determinate_progress)
        layout.addWidget(btn1)

        # テストボタン2: 不定進捗ダイアログ
        btn2 = QPushButton("Indeterminate Progress Dialog をテスト")
        btn2.clicked.connect(self.test_indeterminate_progress)
        layout.addWidget(btn2)

        # テストボタン3: テーマ切り替え
        btn3 = QPushButton("テーマを切り替え (Dark ⇄ Light)")
        btn3.clicked.connect(self.toggle_theme)
        layout.addWidget(btn3)

        central_widget.setLayout(layout)

        # 現在のテーマ
        self.current_theme = ThemeType.DARK

    def test_determinate_progress(self):
        """確定進捗ダイアログをテスト"""
        # ダイアログを作成
        dialog = ProgressDialog(
            parent=self,
            title="テスト進捗",
            total_items=100,
            cancelable=True
        )

        # ワーカースレッドを作成
        self.worker = Worker(total_items=100)
        self.worker.progress.connect(dialog.update_progress)
        self.worker.finished.connect(lambda: dialog.complete("処理が完了しました"))
        self.worker.finished.connect(self.worker.deleteLater)

        # ワーカーを開始
        self.worker.start()

        # ダイアログを表示
        dialog.show()

    def test_indeterminate_progress(self):
        """不定進捗ダイアログをテスト"""
        # ダイアログを作成
        dialog = IndeterminateProgressDialog(
            parent=self,
            title="テスト中",
            message="処理を実行中..."
        )

        # ワーカースレッドを作成（3秒後に自動で閉じる）
        self.worker = QThread()
        self.worker.run = lambda: time.sleep(3)
        self.worker.finished.connect(dialog.close)
        self.worker.finished.connect(self.worker.deleteLater)

        # ワーカーを開始
        self.worker.start()

        # ダイアログを表示
        dialog.show()

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
