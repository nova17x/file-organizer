"""
バックアップ管理
ファイル整理前のバックアップ作成と復元機能を提供
"""

import os
import shutil
import json
from datetime import datetime
from typing import Optional, List, Dict
import uuid


class BackupManager:
    """バックアップを管理するクラス"""

    def __init__(self, backup_dir: str = "data/backups"):
        """
        Args:
            backup_dir: バックアップを保存するディレクトリ
        """
        self.backup_dir = backup_dir

        # バックアップディレクトリが存在しない場合は作成
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self, source_dir: str, backup_name: Optional[str] = None,
                     include_subdirs: bool = True) -> Optional[str]:
        """
        ディレクトリのバックアップを作成

        Args:
            source_dir: バックアップ元のディレクトリ
            backup_name: バックアップの名前（Noneの場合は自動生成）
            include_subdirs: サブディレクトリも含めるか

        Returns:
            バックアップID。エラー時はNone
        """
        try:
            # バックアップIDとメタデータの生成
            backup_id = str(uuid.uuid4())
            timestamp = datetime.now()

            if backup_name is None:
                backup_name = f"backup_{timestamp.strftime('%Y%m%d_%H%M%S')}"

            # バックアップディレクトリの作成
            backup_path = os.path.join(self.backup_dir, backup_id)
            os.makedirs(backup_path, exist_ok=True)

            # ファイル構造のバックアップ
            files_backed_up = []

            if include_subdirs:
                # サブディレクトリを含む完全なバックアップ
                for root, dirs, files in os.walk(source_dir):
                    # 相対パスを計算
                    rel_path = os.path.relpath(root, source_dir)
                    backup_root = os.path.join(backup_path, "files", rel_path)
                    os.makedirs(backup_root, exist_ok=True)

                    for file in files:
                        src_file = os.path.join(root, file)
                        dst_file = os.path.join(backup_root, file)

                        try:
                            shutil.copy2(src_file, dst_file)  # メタデータも保持
                            files_backed_up.append({
                                "original_path": src_file,
                                "relative_path": os.path.join(rel_path, file),
                                "size": os.path.getsize(src_file)
                            })
                        except Exception as e:
                            print(f"警告: ファイルのバックアップに失敗: {src_file} - {e}")

            else:
                # トップレベルのファイルのみバックアップ
                backup_files_dir = os.path.join(backup_path, "files")
                os.makedirs(backup_files_dir, exist_ok=True)

                for item in os.listdir(source_dir):
                    src_file = os.path.join(source_dir, item)
                    if os.path.isfile(src_file):
                        dst_file = os.path.join(backup_files_dir, item)

                        try:
                            shutil.copy2(src_file, dst_file)
                            files_backed_up.append({
                                "original_path": src_file,
                                "relative_path": item,
                                "size": os.path.getsize(src_file)
                            })
                        except Exception as e:
                            print(f"警告: ファイルのバックアップに失敗: {src_file} - {e}")

            # メタデータの保存
            metadata = {
                "backup_id": backup_id,
                "backup_name": backup_name,
                "source_directory": os.path.abspath(source_dir),
                "timestamp": timestamp.isoformat(),
                "include_subdirs": include_subdirs,
                "total_files": len(files_backed_up),
                "total_size": sum(f["size"] for f in files_backed_up),
                "files": files_backed_up
            }

            metadata_path = os.path.join(backup_path, "metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            print(f"バックアップが作成されました: {backup_id}")
            print(f"  ファイル数: {len(files_backed_up)}")
            print(f"  合計サイズ: {self._format_size(metadata['total_size'])}")

            return backup_id

        except PermissionError as e:
            print(f"エラー: アクセス権限がありません: {e}")
            return None
        except Exception as e:
            print(f"エラー: バックアップの作成中にエラーが発生しました: {e}")
            return None

    def list_backups(self) -> List[Dict]:
        """
        利用可能なバックアップの一覧を取得

        Returns:
            バックアップ情報のリスト
        """
        backups = []

        try:
            for item in os.listdir(self.backup_dir):
                backup_path = os.path.join(self.backup_dir, item)
                metadata_path = os.path.join(backup_path, "metadata.json")

                if os.path.isdir(backup_path) and os.path.exists(metadata_path):
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        backups.append({
                            "backup_id": metadata["backup_id"],
                            "backup_name": metadata["backup_name"],
                            "timestamp": metadata["timestamp"],
                            "source_directory": metadata["source_directory"],
                            "total_files": metadata["total_files"],
                            "total_size": metadata["total_size"],
                            "size_formatted": self._format_size(metadata["total_size"])
                        })

            # タイムスタンプで降順ソート
            backups.sort(key=lambda x: x["timestamp"], reverse=True)
            return backups

        except Exception as e:
            print(f"エラー: バックアップ一覧の取得中にエラーが発生しました: {e}")
            return []

    def restore_backup(self, backup_id: str, target_dir: Optional[str] = None,
                      overwrite: bool = False) -> bool:
        """
        バックアップを復元

        Args:
            backup_id: 復元するバックアップのID
            target_dir: 復元先のディレクトリ（Noneの場合は元の場所）
            overwrite: 既存のファイルを上書きするか

        Returns:
            成功したらTrue、失敗したらFalse
        """
        try:
            backup_path = os.path.join(self.backup_dir, backup_id)
            metadata_path = os.path.join(backup_path, "metadata.json")

            if not os.path.exists(metadata_path):
                print(f"エラー: バックアップが見つかりません: {backup_id}")
                return False

            # メタデータの読み込み
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # 復元先ディレクトリの決定
            if target_dir is None:
                target_dir = metadata["source_directory"]

            # 復元先ディレクトリの作成
            os.makedirs(target_dir, exist_ok=True)

            # ファイルの復元
            backup_files_dir = os.path.join(backup_path, "files")
            restored_count = 0
            skipped_count = 0

            for file_info in metadata["files"]:
                rel_path = file_info["relative_path"]
                src_file = os.path.join(backup_files_dir, rel_path)
                dst_file = os.path.join(target_dir, rel_path)

                # 復元先のディレクトリを作成
                dst_dir = os.path.dirname(dst_file)
                os.makedirs(dst_dir, exist_ok=True)

                # ファイルの復元
                if os.path.exists(dst_file) and not overwrite:
                    print(f"スキップ: ファイルが既に存在します: {dst_file}")
                    skipped_count += 1
                    continue

                try:
                    shutil.copy2(src_file, dst_file)
                    restored_count += 1
                except Exception as e:
                    print(f"警告: ファイルの復元に失敗: {dst_file} - {e}")

            print(f"バックアップの復元が完了しました:")
            print(f"  復元されたファイル: {restored_count}")
            print(f"  スキップされたファイル: {skipped_count}")

            return True

        except Exception as e:
            print(f"エラー: バックアップの復元中にエラーが発生しました: {e}")
            return False

    def delete_backup(self, backup_id: str) -> bool:
        """
        バックアップを削除

        Args:
            backup_id: 削除するバックアップのID

        Returns:
            成功したらTrue、失敗したらFalse
        """
        try:
            backup_path = os.path.join(self.backup_dir, backup_id)

            if not os.path.exists(backup_path):
                print(f"エラー: バックアップが見つかりません: {backup_id}")
                return False

            shutil.rmtree(backup_path)
            print(f"バックアップが削除されました: {backup_id}")
            return True

        except Exception as e:
            print(f"エラー: バックアップの削除中にエラーが発生しました: {e}")
            return False

    def cleanup_old_backups(self, keep_count: int = 5) -> int:
        """
        古いバックアップを削除（指定された数だけ保持）

        Args:
            keep_count: 保持するバックアップの数

        Returns:
            削除されたバックアップの数
        """
        backups = self.list_backups()

        if len(backups) <= keep_count:
            print(f"削除するバックアップはありません（現在: {len(backups)}個）")
            return 0

        # 古いバックアップを削除
        deleted_count = 0
        for backup in backups[keep_count:]:
            if self.delete_backup(backup["backup_id"]):
                deleted_count += 1

        print(f"{deleted_count}個の古いバックアップを削除しました")
        return deleted_count

    def get_backup_info(self, backup_id: str) -> Optional[Dict]:
        """
        バックアップの詳細情報を取得

        Args:
            backup_id: バックアップID

        Returns:
            バックアップの詳細情報。エラー時はNone
        """
        try:
            backup_path = os.path.join(self.backup_dir, backup_id)
            metadata_path = os.path.join(backup_path, "metadata.json")

            if not os.path.exists(metadata_path):
                print(f"エラー: バックアップが見つかりません: {backup_id}")
                return None

            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            print(f"エラー: バックアップ情報の取得中にエラーが発生しました: {e}")
            return None

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """
        バイト数を人間が読みやすい形式に変換

        Args:
            size_bytes: バイト数

        Returns:
            フォーマットされたサイズ文字列
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
