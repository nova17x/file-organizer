"""
操作ログ管理
ファイル整理の操作履歴を記録し、元に戻す機能を提供
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
import uuid


class OperationLogger:
    """操作ログを管理するクラス"""

    def __init__(self, log_dir: str = "data/logs"):
        """
        Args:
            log_dir: ログファイルを保存するディレクトリ
        """
        self.log_dir = log_dir
        self.current_operation_id = None
        self.current_actions = []

        # ログディレクトリが存在しない場合は作成
        os.makedirs(self.log_dir, exist_ok=True)

    def start_operation(self) -> str:
        """
        新しい操作セッションを開始

        Returns:
            操作ID
        """
        self.current_operation_id = str(uuid.uuid4())
        self.current_actions = []
        return self.current_operation_id

    def log_action(self, action_type: str, source: str, destination: str,
                   status: str = "success", metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        個別のアクションを記録

        Args:
            action_type: アクションの種類（move, copy, delete など）
            source: 元のファイルパス
            destination: 移動先のファイルパス
            status: 実行結果（success, failed, skipped）
            metadata: 追加のメタデータ
        """
        action = {
            "type": action_type,
            "source": source,
            "destination": destination,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.current_actions.append(action)

    def save_log(self, operation_name: str = "File Organization") -> str:
        """
        現在の操作ログをファイルに保存

        Args:
            operation_name: 操作の名前

        Returns:
            保存したログファイルのパス
        """
        if not self.current_operation_id:
            raise ValueError("操作が開始されていません。start_operation()を先に呼び出してください。")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"operation_{timestamp}_{self.current_operation_id[:8]}.json"
        log_path = os.path.join(self.log_dir, log_filename)

        log_data = {
            "operation_id": self.current_operation_id,
            "operation_name": operation_name,
            "timestamp": datetime.now().isoformat(),
            "total_actions": len(self.current_actions),
            "successful_actions": sum(1 for a in self.current_actions if a["status"] == "success"),
            "failed_actions": sum(1 for a in self.current_actions if a["status"] == "failed"),
            "actions": self.current_actions
        }

        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)

        return log_path

    def get_log(self, log_file: Optional[str] = None, date_range: Optional[tuple] = None) -> Optional[Dict]:
        """
        ログファイルを読み込む

        Args:
            log_file: ログファイルのパス（Noneの場合は最新のログ）
            date_range: 日付範囲のタプル (start_date, end_date)

        Returns:
            ログデータの辞書。エラー時はNone
        """
        try:
            if log_file is None:
                # 最新のログファイルを取得
                log_files = [f for f in os.listdir(self.log_dir) if f.endswith('.json')]
                if not log_files:
                    print("ログファイルが見つかりません。")
                    return None
                log_files.sort(reverse=True)
                log_file = os.path.join(self.log_dir, log_files[0])

            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        except FileNotFoundError:
            print(f"エラー: ログファイルが見つかりません: {log_file}")
            return None
        except json.JSONDecodeError:
            print(f"エラー: ログファイルの形式が不正です: {log_file}")
            return None
        except Exception as e:
            print(f"エラー: ログの読み込み中にエラーが発生しました: {e}")
            return None

    def parse_log_for_undo(self, log_file: str) -> List[Dict[str, str]]:
        """
        ログファイルから元に戻すためのアクションリストを生成

        Args:
            log_file: ログファイルのパス

        Returns:
            元に戻すためのアクションリスト
        """
        log_data = self.get_log(log_file)
        if not log_data:
            return []

        undo_actions = []

        # 成功したアクションのみを逆順で処理
        successful_actions = [a for a in log_data["actions"] if a["status"] == "success"]

        for action in reversed(successful_actions):
            if action["type"] == "move":
                # moveの場合は逆方向に移動
                undo_actions.append({
                    "type": "move",
                    "source": action["destination"],
                    "destination": action["source"]
                })
            elif action["type"] == "copy":
                # copyの場合はコピー先を削除
                undo_actions.append({
                    "type": "delete",
                    "source": action["destination"],
                    "destination": ""
                })
            # 他のアクションタイプも必要に応じて追加

        return undo_actions

    def list_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        ログファイルの一覧を取得

        Args:
            limit: 取得するログファイルの最大数

        Returns:
            ログファイル情報のリスト
        """
        try:
            log_files = [f for f in os.listdir(self.log_dir) if f.endswith('.json')]
            log_files.sort(reverse=True)

            logs_info = []
            for log_file in log_files[:limit]:
                log_path = os.path.join(self.log_dir, log_file)
                log_data = self.get_log(log_path)

                if log_data:
                    logs_info.append({
                        "filename": log_file,
                        "path": log_path,
                        "timestamp": log_data.get("timestamp", ""),
                        "operation_name": log_data.get("operation_name", ""),
                        "total_actions": log_data.get("total_actions", 0),
                        "successful_actions": log_data.get("successful_actions", 0)
                    })

            return logs_info

        except Exception as e:
            print(f"エラー: ログ一覧の取得中にエラーが発生しました: {e}")
            return []

    def export_log(self, log_file: str, output_format: str = 'txt') -> Optional[str]:
        """
        ログを別の形式でエクスポート

        Args:
            log_file: ログファイルのパス
            output_format: 出力形式（txt, csv）

        Returns:
            エクスポートしたファイルのパス。エラー時はNone
        """
        log_data = self.get_log(log_file)
        if not log_data:
            return None

        base_name = os.path.splitext(log_file)[0]
        output_file = f"{base_name}.{output_format}"

        try:
            if output_format == 'txt':
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"操作名: {log_data['operation_name']}\n")
                    f.write(f"日時: {log_data['timestamp']}\n")
                    f.write(f"総アクション数: {log_data['total_actions']}\n")
                    f.write(f"成功: {log_data['successful_actions']}\n")
                    f.write(f"失敗: {log_data['failed_actions']}\n")
                    f.write("\n" + "=" * 80 + "\n\n")

                    for i, action in enumerate(log_data['actions'], 1):
                        f.write(f"[{i}] {action['type'].upper()}\n")
                        f.write(f"  元: {action['source']}\n")
                        f.write(f"  先: {action['destination']}\n")
                        f.write(f"  状態: {action['status']}\n")
                        f.write(f"  時刻: {action['timestamp']}\n\n")

            elif output_format == 'csv':
                import csv
                with open(output_file, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['No', 'Type', 'Source', 'Destination', 'Status', 'Timestamp'])

                    for i, action in enumerate(log_data['actions'], 1):
                        writer.writerow([
                            i,
                            action['type'],
                            action['source'],
                            action['destination'],
                            action['status'],
                            action['timestamp']
                        ])

            return output_file

        except Exception as e:
            print(f"エラー: ログのエクスポート中にエラーが発生しました: {e}")
            return None
