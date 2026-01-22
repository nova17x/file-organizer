"""
ファイル整理マネージャー
ファイルの移動、コピー、整理を実行
"""

import os
import shutil
from typing import List, Dict, Optional, Callable, Any
from .rule_engine import RuleEngine
from utils.logger import OperationLogger


class FileOrganizer:
    """ファイル整理を実行するクラス"""

    def __init__(self, logger: Optional[OperationLogger] = None):
        """
        Args:
            logger: 操作ログを記録するロガー
        """
        self.rule_engine = RuleEngine()
        self.logger = logger or OperationLogger()

    def organize(self, source_dir: str, rules: Dict,
                output_dir: Optional[str] = None,
                preview_mode: bool = False,
                operation_mode: str = 'move') -> List[Dict[str, Any]]:
        """
        ディレクトリを整理してアクションリストを生成

        Args:
            source_dir: 整理対象のディレクトリ
            rules: 適用するルール辞書
            output_dir: 整理先のディレクトリ（Noneの場合はsource_dir内で整理）
            preview_mode: Trueの場合は実行せずにプレビューのみ
            operation_mode: 'move' (移動) または 'copy' (コピー)

        Returns:
            アクションリストの辞書のリスト
        """
        if output_dir is None:
            output_dir = source_dir

        actions = []

        # ルールからカスタム除外パターンを取得
        custom_exclude_patterns = rules.get('exclude_patterns', [])

        try:
            # ソースディレクトリ内のすべてのファイルを取得
            for root, dirs, files in os.walk(source_dir):
                # 除外すべきディレクトリをフィルタリング
                if root != source_dir:
                    if self._should_exclude_directory(root, custom_exclude_patterns):
                        dirs.clear()  # サブディレクトリの探索を停止
                        continue

                for filename in files:
                    source_path = os.path.join(root, filename)

                    # ルールを適用して目的地を決定
                    destination_path = self.rule_engine.apply_rules(
                        source_path,
                        rules,
                        output_dir
                    )

                    if destination_path and destination_path != source_path:
                        actions.append({
                            "type": operation_mode,
                            "source": source_path,
                            "destination": destination_path,
                            "filename": filename,
                            "size": os.path.getsize(source_path),
                            "status": "pending"
                        })

        except Exception as e:
            print(f"エラー: ファイル整理中にエラーが発生しました: {e}")

        return actions

    def execute_actions(self, actions: List[Dict[str, Any]],
                       callback: Optional[Callable[[int, int, str], None]] = None,
                       skip_existing: bool = True) -> Dict[str, Any]:
        """
        アクションリストを実行

        Args:
            actions: organize()で生成されたアクションリスト
            callback: 進捗コールバック関数 (current, total, message)
            skip_existing: 既存のファイルをスキップするか

        Returns:
            実行結果の統計情報
        """
        # 操作を開始
        operation_id = self.logger.start_operation()

        total = len(actions)
        successful = 0
        failed = 0
        skipped = 0

        for i, action in enumerate(actions, 1):
            action_type = action["type"]
            source = action["source"]
            destination = action["destination"]

            # コールバック実行
            if callback:
                callback(i, total, f"処理中: {action['filename']}")

            try:
                # 既存ファイルのチェック
                if os.path.exists(destination):
                    if skip_existing:
                        action["status"] = "skipped"
                        action["reason"] = "ファイルが既に存在します"
                        skipped += 1
                        self.logger.log_action(
                            action_type, source, destination,
                            status="skipped",
                            metadata={"reason": "ファイルが既に存在します"}
                        )
                        continue
                    else:
                        # 既存ファイルに番号を付けて回避
                        destination = self._get_unique_filename(destination)
                        action["destination"] = destination

                # ディレクトリ作成
                dest_dir = os.path.dirname(destination)
                os.makedirs(dest_dir, exist_ok=True)

                # ファイル操作の実行
                if action_type == "move":
                    shutil.move(source, destination)
                elif action_type == "copy":
                    shutil.copy2(source, destination)
                else:
                    raise ValueError(f"不明な操作タイプ: {action_type}")

                action["status"] = "success"
                successful += 1

                # ログ記録
                self.logger.log_action(action_type, source, destination, status="success")

            except PermissionError as e:
                action["status"] = "failed"
                action["error"] = f"アクセス権限がありません: {e}"
                failed += 1
                self.logger.log_action(
                    action_type, source, destination,
                    status="failed",
                    metadata={"error": str(e)}
                )

            except Exception as e:
                action["status"] = "failed"
                action["error"] = str(e)
                failed += 1
                self.logger.log_action(
                    action_type, source, destination,
                    status="failed",
                    metadata={"error": str(e)}
                )

        # ログ保存
        log_path = self.logger.save_log(operation_name="File Organization")

        # 結果を返す
        return {
            "operation_id": operation_id,
            "log_path": log_path,
            "total_actions": total,
            "successful": successful,
            "failed": failed,
            "skipped": skipped,
            "actions": actions
        }

    def undo(self, log_file: str,
            callback: Optional[Callable[[int, int, str], None]] = None) -> bool:
        """
        ログファイルから操作を元に戻す

        Args:
            log_file: ログファイルのパス
            callback: 進捗コールバック関数

        Returns:
            成功したらTrue、失敗したらFalse
        """
        try:
            # 元に戻すアクションを取得
            undo_actions = self.logger.parse_log_for_undo(log_file)

            if not undo_actions:
                print("元に戻すアクションがありません")
                return False

            # 新しい操作として記録開始
            self.logger.start_operation()

            total = len(undo_actions)
            successful = 0

            for i, action in enumerate(undo_actions, 1):
                if callback:
                    filename = os.path.basename(action["source"])
                    callback(i, total, f"元に戻し中: {filename}")

                try:
                    if action["type"] == "move":
                        # ファイルを元の場所に移動
                        source = action["source"]
                        destination = action["destination"]

                        if os.path.exists(source):
                            # 移動先のディレクトリを作成
                            dest_dir = os.path.dirname(destination)
                            os.makedirs(dest_dir, exist_ok=True)

                            shutil.move(source, destination)
                            successful += 1
                            self.logger.log_action("undo_move", source, destination, status="success")

                    elif action["type"] == "delete":
                        # 削除されたファイルは復元できない
                        print(f"警告: 削除されたファイルは復元できません: {action['source']}")

                except Exception as e:
                    print(f"エラー: 元に戻す処理中にエラーが発生しました: {e}")
                    self.logger.log_action(
                        "undo_" + action["type"],
                        action["source"],
                        action["destination"],
                        status="failed",
                        metadata={"error": str(e)}
                    )

            # ログ保存
            self.logger.save_log(operation_name="Undo Operation")

            print(f"元に戻し完了: {successful}/{total} 件")

            # 空のディレクトリを削除
            # 整理時に作成されたディレクトリを取得
            created_dirs = set()
            for action in undo_actions:
                if action["type"] == "move":
                    # 移動元のディレクトリ（整理先）
                    source_dir = os.path.dirname(action["source"])
                    created_dirs.add(source_dir)

            # 空のディレクトリを削除
            for dir_path in sorted(created_dirs, key=len, reverse=True):
                self._remove_empty_directories(dir_path)

            return successful > 0

        except Exception as e:
            print(f"エラー: 元に戻す処理中にエラーが発生しました: {e}")
            return False

    def _remove_empty_directories(self, start_path: str) -> None:
        """
        空のディレクトリを再帰的に削除

        Args:
            start_path: 開始ディレクトリのパス
        """
        try:
            # ディレクトリが存在するか確認
            if not os.path.exists(start_path) or not os.path.isdir(start_path):
                return

            # ディレクトリが空かチェック
            while os.path.exists(start_path) and os.path.isdir(start_path):
                try:
                    # サブディレクトリやファイルがあるかチェック
                    if not os.listdir(start_path):
                        # 空なら削除
                        os.rmdir(start_path)
                        print(f"空のディレクトリを削除: {start_path}")
                        # 親ディレクトリも空かチェック
                        start_path = os.path.dirname(start_path)
                    else:
                        # 空でない場合は終了
                        break
                except OSError:
                    # 削除できない場合は終了
                    break

        except Exception as e:
            print(f"警告: ディレクトリ削除中にエラーが発生しました: {e}")

    def create_directory_structure(self, base_dir: str, categories: List[str]) -> None:
        """
        カテゴリに基づいてディレクトリ構造を作成

        Args:
            base_dir: ベースディレクトリ
            categories: カテゴリ名のリスト
        """
        try:
            for category in categories:
                category_path = os.path.join(base_dir, category)
                os.makedirs(category_path, exist_ok=True)

            print(f"{len(categories)}個のカテゴリディレクトリを作成しました")

        except Exception as e:
            print(f"エラー: ディレクトリ構造の作成中にエラーが発生しました: {e}")

    def get_statistics(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        アクションリストから統計情報を取得

        Args:
            actions: アクションリスト

        Returns:
            統計情報の辞書
        """
        total_size = sum(action.get("size", 0) for action in actions)
        by_type = {}
        by_status = {}

        for action in actions:
            # タイプ別
            action_type = action.get("type", "unknown")
            by_type[action_type] = by_type.get(action_type, 0) + 1

            # ステータス別
            status = action.get("status", "pending")
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "total_actions": len(actions),
            "total_size": total_size,
            "total_size_formatted": self._format_size(total_size),
            "by_type": by_type,
            "by_status": by_status
        }

    def _should_exclude_directory(self, path: str, custom_patterns: List[str] = None) -> bool:
        """
        ディレクトリを除外すべきかどうかを判定

        Args:
            path: ディレクトリのパス
            custom_patterns: カスタム除外パターンのリスト

        Returns:
            除外すべき場合True
        """
        dirname = os.path.basename(path)

        # デフォルトの除外パターン
        # 1. 整理カテゴリディレクトリ（このツールが作成するディレクトリ）
        organized_patterns = [
            "Images", "Videos", "Documents", "Audio", "Archives",
            "Code", "Others", "Small", "Medium", "Large"
        ]

        # 2. システムおよび開発関連ディレクトリ
        system_patterns = [
            # バージョン管理
            ".git", ".svn", ".hg", ".bzr",
            # Python
            "__pycache__", ".pytest_cache", ".mypy_cache", ".tox",
            "venv", ".venv", "env", ".env", "virtualenv",
            # Node.js
            "node_modules", "bower_components",
            # その他の開発ツール
            ".idea", ".vscode", ".vs",
            # システムフォルダ
            "bin", "lib", "lib64", "include", "share",
            # macOS
            ".DS_Store", ".Trash", ".Spotlight-V100",
            # Windows
            "$RECYCLE.BIN", "System Volume Information",
            # ビルド成果物
            "build", "dist", "target", "out",
            # キャッシュ
            ".cache", "cache", "tmp", "temp",
        ]

        # 3. 隠しディレクトリ（.で始まる）
        if dirname.startswith('.'):
            return True

        # 4. デフォルトパターンに一致するか
        if dirname in organized_patterns or dirname in system_patterns:
            return True

        # 5. カスタムパターンに一致するか
        if custom_patterns:
            for pattern in custom_patterns:
                # 完全一致または部分一致（簡易的なパターンマッチング）
                if pattern in dirname or dirname == pattern:
                    return True

        return False

    def _get_unique_filename(self, file_path: str) -> str:
        """
        重複しないファイル名を生成

        Args:
            file_path: 元のファイルパス

        Returns:
            ユニークなファイルパス
        """
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)

        counter = 1
        while os.path.exists(file_path):
            new_filename = f"{name}_{counter}{ext}"
            file_path = os.path.join(directory, new_filename)
            counter += 1

        return file_path

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """
        バイト数を人間が読みやすい形式に変換
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
