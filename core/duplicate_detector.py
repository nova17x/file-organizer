"""
重複ファイル検出
ハッシュ値を使用して重複ファイルを検出
"""

import os
from typing import List, Dict, Optional, Set
from collections import defaultdict
from utils.hash_utils import calculate_file_hash, get_quick_file_signature


class DuplicateDetector:
    """重複ファイルを検出するクラス"""

    def __init__(self, hash_algorithm: str = 'sha256'):
        """
        Args:
            hash_algorithm: 使用するハッシュアルゴリズム
        """
        self.hash_algorithm = hash_algorithm
        self.file_cache = {}  # ファイルパス: ハッシュ値のキャッシュ

    def scan_directory(self, path: str, recursive: bool = True,
                      include_hidden: bool = False,
                      extensions: Optional[Set[str]] = None) -> List[str]:
        """
        ディレクトリをスキャンしてファイル一覧を取得

        Args:
            path: スキャンするディレクトリのパス
            recursive: サブディレクトリも含めるか
            include_hidden: 隠しファイルを含めるか
            extensions: 対象とする拡張子のセット（Noneの場合は全て）

        Returns:
            ファイルパスのリスト
        """
        files = []

        try:
            if recursive:
                for root, dirs, filenames in os.walk(path):
                    # 隠しディレクトリをスキップ
                    if not include_hidden:
                        dirs[:] = [d for d in dirs if not d.startswith('.')]

                    for filename in filenames:
                        # 隠しファイルをスキップ
                        if not include_hidden and filename.startswith('.'):
                            continue

                        file_path = os.path.join(root, filename)

                        # 拡張子フィルタ
                        if extensions:
                            _, ext = os.path.splitext(filename)
                            if ext.lower() not in extensions:
                                continue

                        if os.path.isfile(file_path):
                            files.append(file_path)
            else:
                for item in os.listdir(path):
                    # 隠しファイルをスキップ
                    if not include_hidden and item.startswith('.'):
                        continue

                    file_path = os.path.join(path, item)

                    if os.path.isfile(file_path):
                        # 拡張子フィルタ
                        if extensions:
                            _, ext = os.path.splitext(item)
                            if ext.lower() not in extensions:
                                continue

                        files.append(file_path)

        except PermissionError as e:
            print(f"警告: アクセス権限がありません: {path}")
        except Exception as e:
            print(f"エラー: ディレクトリのスキャン中にエラーが発生しました: {e}")

        return files

    def find_duplicates(self, file_list: List[str],
                       use_quick_scan: bool = True) -> Dict[str, List[str]]:
        """
        ファイルリストから重複を検出

        Args:
            file_list: ファイルパスのリスト
            use_quick_scan: 高速スキャン（サイズと部分ハッシュで事前フィルタ）

        Returns:
            重複グループの辞書 {ハッシュ値: [ファイルパスリスト]}
        """
        if use_quick_scan:
            return self._find_duplicates_quick(file_list)
        else:
            return self._find_duplicates_full(file_list)

    def _find_duplicates_quick(self, file_list: List[str]) -> Dict[str, List[str]]:
        """
        高速な重複検出（2段階スキャン）

        1段階目: ファイルサイズと部分ハッシュで候補を絞る
        2段階目: 候補のみ完全なハッシュで確認
        """
        # 1段階目: 高速シグネチャでグループ化
        signature_groups = defaultdict(list)

        print("1段階目: 高速スキャン中...")
        for i, file_path in enumerate(file_list, 1):
            if i % 100 == 0:
                print(f"  処理中: {i}/{len(file_list)}")

            signature = get_quick_file_signature(file_path)
            if signature:
                signature_groups[signature].append(file_path)

        # 2段階目: 重複候補のみ完全なハッシュを計算
        duplicates = {}
        candidates = [files for files in signature_groups.values() if len(files) > 1]

        if candidates:
            print(f"2段階目: {sum(len(group) for group in candidates)}個の候補を詳細スキャン中...")
            for group in candidates:
                hash_groups = defaultdict(list)

                for file_path in group:
                    file_hash = self._get_file_hash(file_path)
                    if file_hash:
                        hash_groups[file_hash].append(file_path)

                # 実際に重複しているグループのみ追加
                for file_hash, files in hash_groups.items():
                    if len(files) > 1:
                        duplicates[file_hash] = files

        return duplicates

    def _find_duplicates_full(self, file_list: List[str]) -> Dict[str, List[str]]:
        """
        完全な重複検出（全ファイルのハッシュを計算）
        """
        hash_groups = defaultdict(list)

        print("完全スキャン中...")
        for i, file_path in enumerate(file_list, 1):
            if i % 50 == 0:
                print(f"  処理中: {i}/{len(file_list)}")

            file_hash = self._get_file_hash(file_path)
            if file_hash:
                hash_groups[file_hash].append(file_path)

        # 重複しているグループのみを返す
        return {h: files for h, files in hash_groups.items() if len(files) > 1}

    def _get_file_hash(self, file_path: str) -> Optional[str]:
        """
        ファイルのハッシュを取得（キャッシュを使用）

        Args:
            file_path: ファイルのパス

        Returns:
            ハッシュ値。エラー時はNone
        """
        # キャッシュをチェック
        if file_path in self.file_cache:
            return self.file_cache[file_path]

        # ハッシュを計算
        file_hash = calculate_file_hash(file_path, self.hash_algorithm)
        if file_hash:
            self.file_cache[file_path] = file_hash

        return file_hash

    def suggest_actions(self, duplicate_groups: Dict[str, List[str]],
                       keep_strategy: str = 'newest') -> List[Dict]:
        """
        重複ファイルに対する推奨アクションを生成

        Args:
            duplicate_groups: find_duplicates()の結果
            keep_strategy: 保持するファイルの選択戦略
                          'newest' (最新), 'oldest' (最古),
                          'shortest_path' (最短パス), 'longest_path' (最長パス)

        Returns:
            アクション提案のリスト
        """
        suggestions = []

        for file_hash, file_paths in duplicate_groups.items():
            if len(file_paths) < 2:
                continue

            # 保持するファイルを選択
            keep_file = self._select_file_to_keep(file_paths, keep_strategy)

            # 削除候補を特定
            delete_candidates = [f for f in file_paths if f != keep_file]

            suggestions.append({
                "hash": file_hash,
                "keep": keep_file,
                "delete": delete_candidates,
                "total_duplicates": len(file_paths),
                "can_free": self._calculate_space_saving(delete_candidates),
                "reason": self._get_keep_reason(keep_strategy)
            })

        return suggestions

    def _select_file_to_keep(self, file_paths: List[str], strategy: str) -> str:
        """
        保持するファイルを選択

        Args:
            file_paths: ファイルパスのリスト
            strategy: 選択戦略

        Returns:
            保持するファイルのパス
        """
        if strategy == 'newest':
            # 最新のファイルを保持
            return max(file_paths, key=lambda f: os.path.getmtime(f))

        elif strategy == 'oldest':
            # 最古のファイルを保持
            return min(file_paths, key=lambda f: os.path.getmtime(f))

        elif strategy == 'shortest_path':
            # 最短パスのファイルを保持
            return min(file_paths, key=len)

        elif strategy == 'longest_path':
            # 最長パスのファイルを保持
            return max(file_paths, key=len)

        else:
            # デフォルトは最初のファイル
            return file_paths[0]

    def _calculate_space_saving(self, file_paths: List[str]) -> int:
        """
        削除によって節約できる容量を計算

        Args:
            file_paths: 削除候補のファイルパスリスト

        Returns:
            節約できるバイト数
        """
        total = 0
        for file_path in file_paths:
            try:
                total += os.path.getsize(file_path)
            except Exception:
                continue
        return total

    @staticmethod
    def _get_keep_reason(strategy: str) -> str:
        """
        保持戦略の説明を取得

        Args:
            strategy: 戦略名

        Returns:
            説明文
        """
        reasons = {
            'newest': '最新のファイルを保持',
            'oldest': '最古のファイルを保持',
            'shortest_path': '最短パスのファイルを保持',
            'longest_path': '最長パスのファイルを保持'
        }
        return reasons.get(strategy, '最初のファイルを保持')

    def get_duplicate_statistics(self, duplicate_groups: Dict[str, List[str]]) -> Dict:
        """
        重複ファイルの統計情報を取得

        Args:
            duplicate_groups: find_duplicates()の結果

        Returns:
            統計情報の辞書
        """
        total_files = sum(len(files) for files in duplicate_groups.values())
        unique_files = len(duplicate_groups)
        duplicate_files = total_files - unique_files

        total_size = 0
        wasted_space = 0

        for files in duplicate_groups.values():
            if files:
                try:
                    file_size = os.path.getsize(files[0])
                    total_size += file_size * len(files)
                    wasted_space += file_size * (len(files) - 1)
                except Exception:
                    continue

        return {
            "total_duplicate_sets": len(duplicate_groups),
            "total_files": total_files,
            "unique_files": unique_files,
            "duplicate_files": duplicate_files,
            "total_size_bytes": total_size,
            "wasted_space_bytes": wasted_space,
            "wasted_space_formatted": self._format_size(wasted_space)
        }

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

    def clear_cache(self) -> None:
        """ハッシュキャッシュをクリア"""
        self.file_cache.clear()
