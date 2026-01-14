"""
ハッシュ計算ユーティリティ
ファイルの重複検出に使用するハッシュ値を計算
"""

import hashlib
from typing import Optional


def calculate_file_hash(file_path: str, algorithm: str = 'sha256', chunk_size: int = 8192) -> Optional[str]:
    """
    ファイルのハッシュ値を計算

    Args:
        file_path: ハッシュを計算するファイルのパス
        algorithm: 使用するハッシュアルゴリズム（md5, sha1, sha256など）
        chunk_size: 一度に読み込むバイト数（メモリ効率のため）

    Returns:
        ハッシュ値の16進数文字列。エラー時はNone
    """
    try:
        # ハッシュオブジェクトの作成
        hash_obj = hashlib.new(algorithm)

        # ファイルをチャンクごとに読み込んでハッシュを更新
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()

    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {file_path}")
        return None
    except PermissionError:
        print(f"エラー: ファイルへのアクセス権限がありません: {file_path}")
        return None
    except Exception as e:
        print(f"エラー: ハッシュ計算中にエラーが発生しました: {e}")
        return None


def hash_file_chunks(file_path: str, num_chunks: int = 3, chunk_size: int = 8192) -> Optional[str]:
    """
    ファイルの一部分のみを使用した高速ハッシュ計算
    大きなファイルの高速比較に使用（完全な一致確認には不適切）

    Args:
        file_path: ハッシュを計算するファイルのパス
        num_chunks: サンプリングするチャンク数（先頭、中央、末尾）
        chunk_size: 各チャンクのバイト数

    Returns:
        部分ハッシュ値の16進数文字列。エラー時はNone
    """
    try:
        hash_obj = hashlib.sha256()

        with open(file_path, 'rb') as f:
            # ファイルサイズを取得
            f.seek(0, 2)  # ファイル末尾に移動
            file_size = f.tell()

            if file_size == 0:
                return hashlib.sha256(b'').hexdigest()

            # サンプリング位置を計算
            positions = []
            if num_chunks >= 1:
                positions.append(0)  # 先頭
            if num_chunks >= 2 and file_size > chunk_size:
                positions.append(file_size // 2)  # 中央
            if num_chunks >= 3 and file_size > chunk_size * 2:
                positions.append(max(0, file_size - chunk_size))  # 末尾

            # 各位置からチャンクを読み込んでハッシュを更新
            for pos in positions:
                f.seek(pos)
                chunk = f.read(chunk_size)
                hash_obj.update(chunk)

        return hash_obj.hexdigest()

    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {file_path}")
        return None
    except PermissionError:
        print(f"エラー: ファイルへのアクセス権限がありません: {file_path}")
        return None
    except Exception as e:
        print(f"エラー: 部分ハッシュ計算中にエラーが発生しました: {e}")
        return None


def get_quick_file_signature(file_path: str) -> Optional[tuple]:
    """
    ファイルの高速シグネチャを取得（サイズ + 部分ハッシュ）
    大量のファイル比較の第一段階として使用

    Args:
        file_path: ファイルのパス

    Returns:
        (ファイルサイズ, 部分ハッシュ) のタプル。エラー時はNone
    """
    try:
        import os
        file_size = os.path.getsize(file_path)
        partial_hash = hash_file_chunks(file_path, num_chunks=2, chunk_size=4096)

        if partial_hash is None:
            return None

        return (file_size, partial_hash)

    except Exception as e:
        print(f"エラー: ファイルシグネチャ取得中にエラーが発生しました: {e}")
        return None
