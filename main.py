#!/usr/bin/env python3
"""
File Organizer - ファイル整理ツール

フル機能のファイル整理アプリケーション
- 拡張子別、日付別、サイズ別、パターン別の分類
- 重複ファイル検出
- バックアップと元に戻す機能
- フォルダ監視による自動整理
- GUI操作
"""

import sys
import os

# モジュールのパスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import MainWindow
from config import settings


def main():
    """アプリケーションのエントリーポイント"""
    try:
        # 必要なディレクトリの確認
        settings.ensure_directories()

        # メインウィンドウを作成
        app = MainWindow()

        # イベントループを開始
        app.mainloop()

    except KeyboardInterrupt:
        print("\n\nアプリケーションを終了します...")
        sys.exit(0)

    except Exception as e:
        print(f"エラー: アプリケーションの起動中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
