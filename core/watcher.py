"""
フォルダ監視
ファイルの作成・変更を監視して自動整理
"""

import os
import time
from typing import Dict, Optional, Callable, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from .file_manager import FileOrganizer


class FileEventHandler(FileSystemEventHandler):
    """ファイルシステムイベントを処理するハンドラー"""

    def __init__(self, rules: Dict, organizer: FileOrganizer,
                 callback: Optional[Callable[[str, str], None]] = None,
                 delay: float = 2.0):
        """
        Args:
            rules: 適用するルール辞書
            organizer: FileOrganizerインスタンス
            callback: イベント発生時のコールバック関数
            delay: ファイル作成後の待機時間（秒）
        """
        super().__init__()
        self.rules = rules
        self.organizer = organizer
        self.callback = callback
        self.delay = delay
        self.processing = set()  # 処理中のファイルパス

    def on_created(self, event: FileSystemEvent) -> None:
        """
        ファイル作成時の処理

        Args:
            event: ファイルシステムイベント
        """
        if event.is_directory:
            return

        file_path = event.src_path

        # 既に処理中のファイルはスキップ
        if file_path in self.processing:
            return

        # 整理対象外のファイルはスキップ
        if self._should_ignore(file_path):
            return

        # コールバック実行
        if self.callback:
            self.callback("created", file_path)

        # 少し待機（ファイルの書き込みが完了するまで）
        time.sleep(self.delay)

        # ファイルを整理
        self._organize_file(file_path)

    def on_modified(self, event: FileSystemEvent) -> None:
        """
        ファイル変更時の処理

        Args:
            event: ファイルシステムイベント
        """
        # 変更イベントは頻繁に発生するため、作成時のみ処理
        pass

    def _organize_file(self, file_path: str) -> None:
        """
        個別のファイルを整理

        Args:
            file_path: ファイルのパス
        """
        try:
            self.processing.add(file_path)

            # ファイルが存在するか確認
            if not os.path.exists(file_path):
                return

            # 整理先を決定
            source_dir = os.path.dirname(file_path)
            destination = self.organizer.rule_engine.apply_rules(
                file_path,
                self.rules,
                source_dir
            )

            if destination and destination != file_path:
                # 移動を実行
                actions = [{
                    "type": "move",
                    "source": file_path,
                    "destination": destination,
                    "filename": os.path.basename(file_path),
                    "size": os.path.getsize(file_path),
                    "status": "pending"
                }]

                result = self.organizer.execute_actions(actions)

                if result["successful"] > 0:
                    print(f"自動整理: {os.path.basename(file_path)} → {destination}")
                    if self.callback:
                        self.callback("organized", destination)

        except Exception as e:
            print(f"エラー: ファイルの自動整理中にエラーが発生しました: {e}")

        finally:
            # 処理完了
            if file_path in self.processing:
                self.processing.remove(file_path)

    def _should_ignore(self, file_path: str) -> bool:
        """
        ファイルを無視すべきかどうかを判定

        Args:
            file_path: ファイルのパス

        Returns:
            無視する場合True
        """
        filename = os.path.basename(file_path)

        # 隠しファイル
        if filename.startswith('.'):
            return True

        # 一時ファイル
        if filename.endswith(('.tmp', '.temp', '.crdownload', '.part')):
            return True

        # システムファイル
        system_files = ['Thumbs.db', 'desktop.ini', '.DS_Store']
        if filename in system_files:
            return True

        return False


class FolderWatcher:
    """フォルダを監視して自動整理を行うクラス"""

    def __init__(self, organizer: Optional[FileOrganizer] = None):
        """
        Args:
            organizer: FileOrganizerインスタンス
        """
        self.organizer = organizer or FileOrganizer()
        self.observer: Optional[Observer] = None
        self.is_watching = False
        self.watched_path: Optional[str] = None

    def start_watching(self, path: str, rules: Dict,
                      callback: Optional[Callable[[str, str], None]] = None,
                      recursive: bool = True,
                      delay: float = 2.0) -> bool:
        """
        フォルダの監視を開始

        Args:
            path: 監視するディレクトリのパス
            rules: 適用するルール辞書
            callback: イベント発生時のコールバック関数 (event_type, file_path)
            recursive: サブディレクトリも監視するか
            delay: ファイル作成後の待機時間（秒）

        Returns:
            成功したらTrue、失敗したらFalse
        """
        try:
            # 既に監視中の場合は停止
            if self.is_watching:
                self.stop_watching()

            # パスの検証
            if not os.path.exists(path):
                print(f"エラー: ディレクトリが存在しません: {path}")
                return False

            if not os.path.isdir(path):
                print(f"エラー: 指定されたパスはディレクトリではありません: {path}")
                return False

            # イベントハンドラーの作成
            event_handler = FileEventHandler(
                rules=rules,
                organizer=self.organizer,
                callback=callback,
                delay=delay
            )

            # オブザーバーの作成と開始
            self.observer = Observer()
            self.observer.schedule(event_handler, path, recursive=recursive)
            self.observer.start()

            self.is_watching = True
            self.watched_path = path

            print(f"フォルダ監視を開始しました: {path}")
            if recursive:
                print("  サブディレクトリも監視します")

            return True

        except Exception as e:
            print(f"エラー: フォルダ監視の開始中にエラーが発生しました: {e}")
            return False

    def stop_watching(self) -> bool:
        """
        フォルダの監視を停止

        Returns:
            成功したらTrue、失敗したらFalse
        """
        try:
            if not self.is_watching or not self.observer:
                print("監視は実行されていません")
                return False

            self.observer.stop()
            self.observer.join(timeout=5)

            self.is_watching = False
            print(f"フォルダ監視を停止しました: {self.watched_path}")
            self.watched_path = None

            return True

        except Exception as e:
            print(f"エラー: フォルダ監視の停止中にエラーが発生しました: {e}")
            return False

    def is_active(self) -> bool:
        """
        監視が実行中かどうかを確認

        Returns:
            実行中の場合True
        """
        return self.is_watching and self.observer is not None and self.observer.is_alive()

    def get_status(self) -> Dict[str, any]:
        """
        監視の状態を取得

        Returns:
            状態情報の辞書
        """
        return {
            "is_watching": self.is_watching,
            "is_active": self.is_active(),
            "watched_path": self.watched_path
        }


class WatcherManager:
    """複数のフォルダ監視を管理するクラス"""

    def __init__(self):
        """複数のウォッチャーを管理"""
        self.watchers: Dict[str, FolderWatcher] = {}

    def add_watcher(self, name: str, path: str, rules: Dict,
                   callback: Optional[Callable[[str, str], None]] = None,
                   recursive: bool = True) -> bool:
        """
        新しいウォッチャーを追加

        Args:
            name: ウォッチャーの名前
            path: 監視するパス
            rules: 適用するルール
            callback: コールバック関数
            recursive: 再帰的に監視するか

        Returns:
            成功したらTrue
        """
        if name in self.watchers:
            print(f"警告: '{name}'という名前のウォッチャーは既に存在します")
            return False

        watcher = FolderWatcher()
        if watcher.start_watching(path, rules, callback, recursive):
            self.watchers[name] = watcher
            return True

        return False

    def remove_watcher(self, name: str) -> bool:
        """
        ウォッチャーを削除

        Args:
            name: ウォッチャーの名前

        Returns:
            成功したらTrue
        """
        if name not in self.watchers:
            print(f"エラー: '{name}'という名前のウォッチャーは存在しません")
            return False

        watcher = self.watchers[name]
        watcher.stop_watching()
        del self.watchers[name]

        return True

    def stop_all(self) -> None:
        """すべてのウォッチャーを停止"""
        for name, watcher in list(self.watchers.items()):
            watcher.stop_watching()

        self.watchers.clear()
        print("すべてのウォッチャーを停止しました")

    def get_all_status(self) -> Dict[str, Dict]:
        """
        すべてのウォッチャーの状態を取得

        Returns:
            ウォッチャー名: 状態情報 の辞書
        """
        return {name: watcher.get_status() for name, watcher in self.watchers.items()}

    def list_watchers(self) -> List[str]:
        """
        ウォッチャー名のリストを取得

        Returns:
            ウォッチャー名のリスト
        """
        return list(self.watchers.keys())
