#!/usr/bin/env python3
"""
プレビュー機能のデバッグスクリプト
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui import MainWindow, ThemeManager, ThemeType

def main():
    app = QApplication(sys.argv)
    ThemeManager.apply_theme(app, ThemeType.DARK)

    window = MainWindow()

    # デバッグ: ソースディレクトリとルールを自動設定
    import os
    test_dir = os.path.expanduser("~/Downloads")
    if os.path.exists(test_dir):
        window.source_dir_edit.setText(test_dir)
        print(f"ソースディレクトリ設定: {test_dir}")

    # デフォルトルールが読み込まれているか確認
    if window.current_rules:
        print(f"ルール設定済み: {window.current_rules.get('name', '不明')}")
    else:
        print("警告: ルールが設定されていません")

    # プレビューボタンを手動でトリガー
    def test_preview():
        print("プレビューボタンをクリック")
        window._preview_organization()

    # 2秒後に自動テスト
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(2000, test_preview)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
