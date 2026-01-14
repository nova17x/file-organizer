"""
ルールエンジン
整理ルールの読み込み、保存、検証、適用を管理
"""

import json
import os
from typing import Dict, List, Optional, Tuple, Any
from .classifier import FileClassifier


class RuleEngine:
    """整理ルールを管理するクラス"""

    def __init__(self, rules_dir: str = "data/rules"):
        """
        Args:
            rules_dir: ルールファイルを保存するディレクトリ
        """
        self.rules_dir = rules_dir
        self.classifier = FileClassifier()

        # ルールディレクトリが存在しない場合は作成
        os.makedirs(self.rules_dir, exist_ok=True)

    def load_rules(self, rule_path: str) -> Optional[Dict]:
        """
        ルールファイルを読み込む

        Args:
            rule_path: ルールファイルのパス

        Returns:
            ルールデータの辞書。エラー時はNone
        """
        try:
            with open(rule_path, 'r', encoding='utf-8') as f:
                rules = json.load(f)

            # ルールの検証
            is_valid, errors = self.validate_rules(rules)
            if not is_valid:
                print(f"警告: ルールファイルに問題があります:")
                for error in errors:
                    print(f"  - {error}")

            return rules

        except FileNotFoundError:
            print(f"エラー: ルールファイルが見つかりません: {rule_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"エラー: ルールファイルのJSON形式が不正です: {e}")
            return None
        except Exception as e:
            print(f"エラー: ルールファイルの読み込み中にエラーが発生しました: {e}")
            return None

    def save_rules(self, rules_dict: Dict, rule_path: str) -> bool:
        """
        ルールをファイルに保存

        Args:
            rules_dict: ルールデータの辞書
            rule_path: 保存先のパス

        Returns:
            成功したらTrue、失敗したらFalse
        """
        try:
            # ルールの検証
            is_valid, errors = self.validate_rules(rules_dict)
            if not is_valid:
                print("エラー: 無効なルールです:")
                for error in errors:
                    print(f"  - {error}")
                return False

            # JSONとして保存
            with open(rule_path, 'w', encoding='utf-8') as f:
                json.dump(rules_dict, f, ensure_ascii=False, indent=2)

            print(f"ルールが保存されました: {rule_path}")
            return True

        except Exception as e:
            print(f"エラー: ルールの保存中にエラーが発生しました: {e}")
            return False

    def validate_rules(self, rules_dict: Dict) -> Tuple[bool, List[str]]:
        """
        ルールの妥当性を検証

        Args:
            rules_dict: ルールデータの辞書

        Returns:
            (検証結果, エラーメッセージリスト) のタプル
        """
        errors = []

        # 必須フィールドの確認
        if "name" not in rules_dict:
            errors.append("'name' フィールドが必要です")

        if "rules" not in rules_dict:
            errors.append("'rules' フィールドが必要です")
            return False, errors

        if not isinstance(rules_dict["rules"], list):
            errors.append("'rules' はリストである必要があります")
            return False, errors

        # 各ルールの検証
        for i, rule in enumerate(rules_dict["rules"]):
            if not isinstance(rule, dict):
                errors.append(f"ルール{i+1}: ルールは辞書である必要があります")
                continue

            rule_type = rule.get("type")
            if not rule_type:
                errors.append(f"ルール{i+1}: 'type' フィールドが必要です")
                continue

            # タイプ別の検証
            if rule_type == "extension":
                if "categories" not in rule:
                    errors.append(f"ルール{i+1}: 'categories' フィールドが必要です")
                elif not isinstance(rule["categories"], dict):
                    errors.append(f"ルール{i+1}: 'categories' は辞書である必要があります")

            elif rule_type == "date":
                if "mode" in rule and rule["mode"] not in ["created", "modified"]:
                    errors.append(f"ルール{i+1}: 'mode' は 'created' または 'modified' である必要があります")

            elif rule_type == "size":
                if "thresholds" not in rule:
                    errors.append(f"ルール{i+1}: 'thresholds' フィールドが必要です")
                elif not isinstance(rule["thresholds"], dict):
                    errors.append(f"ルール{i+1}: 'thresholds' は辞書である必要があります")

            elif rule_type == "pattern":
                if "patterns" not in rule:
                    errors.append(f"ルール{i+1}: 'patterns' フィールドが必要です")
                elif not isinstance(rule["patterns"], dict):
                    errors.append(f"ルール{i+1}: 'patterns' は辞書である必要があります")

            else:
                errors.append(f"ルール{i+1}: 不明なルールタイプ '{rule_type}'")

        is_valid = len(errors) == 0
        return is_valid, errors

    def apply_rules(self, file_path: str, rules_dict: Dict,
                   base_dir: str = ".") -> Optional[str]:
        """
        ファイルにルールを適用して目的地パスを取得

        Args:
            file_path: ファイルのパス
            rules_dict: ルールデータの辞書
            base_dir: 整理先のベースディレクトリ

        Returns:
            目的地のパス。エラー時はNone
        """
        try:
            # 拡張子カテゴリの更新（ルールに含まれる場合）
            for rule in rules_dict.get("rules", []):
                if rule.get("type") == "extension" and "categories" in rule:
                    for category, extensions in rule["categories"].items():
                        self.classifier.add_category(category, extensions)

            # ファイルを分類
            classification = self.classifier.classify_multi(
                file_path,
                rules_dict.get("rules", [])
            )

            # 優先順位の取得
            priority = rules_dict.get("priority", ["pattern", "extension", "date", "size"])

            # 目的地パスの生成
            destination = self.classifier.get_destination_path(
                file_path,
                base_dir,
                classification,
                priority
            )

            return destination

        except Exception as e:
            print(f"エラー: ルールの適用中にエラーが発生しました: {e}")
            return None

    def create_default_rule(self, rule_name: str = "Default Rule") -> Dict:
        """
        デフォルトのルールセットを作成

        Args:
            rule_name: ルールの名前

        Returns:
            デフォルトのルール辞書
        """
        return {
            "name": rule_name,
            "version": "1.0",
            "description": "デフォルトのファイル整理ルール",
            "priority": ["pattern", "extension", "date"],
            "rules": [
                {
                    "type": "extension",
                    "enabled": True,
                    "categories": {
                        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
                        "Videos": [".mp4", ".avi", ".mkv", ".mov"],
                        "Documents": [".pdf", ".doc", ".docx", ".txt"],
                        "Audio": [".mp3", ".wav", ".flac", ".aac"],
                        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"]
                    }
                },
                {
                    "type": "date",
                    "enabled": True,
                    "mode": "modified",
                    "format": "%Y/%m"
                },
                {
                    "type": "pattern",
                    "enabled": True,
                    "patterns": {
                        "Screenshots": "^screenshot[_-].*",
                        "Camera": "^(IMG|DSC|DCIM)[_-].*",
                        "Downloads": "^download.*"
                    }
                }
            ]
        }

    def list_rules(self) -> List[Dict[str, str]]:
        """
        保存されているルールファイルの一覧を取得

        Returns:
            ルールファイル情報のリスト
        """
        rules = []

        try:
            for filename in os.listdir(self.rules_dir):
                if filename.endswith('.json'):
                    rule_path = os.path.join(self.rules_dir, filename)
                    rule_data = self.load_rules(rule_path)

                    if rule_data:
                        rules.append({
                            "filename": filename,
                            "path": rule_path,
                            "name": rule_data.get("name", "名前なし"),
                            "description": rule_data.get("description", ""),
                            "version": rule_data.get("version", "1.0")
                        })

            return rules

        except Exception as e:
            print(f"エラー: ルール一覧の取得中にエラーが発生しました: {e}")
            return []

    def delete_rule(self, rule_path: str) -> bool:
        """
        ルールファイルを削除

        Args:
            rule_path: 削除するルールファイルのパス

        Returns:
            成功したらTrue、失敗したらFalse
        """
        try:
            if os.path.exists(rule_path):
                os.remove(rule_path)
                print(f"ルールが削除されました: {rule_path}")
                return True
            else:
                print(f"エラー: ルールファイルが見つかりません: {rule_path}")
                return False

        except Exception as e:
            print(f"エラー: ルールの削除中にエラーが発生しました: {e}")
            return False

    def merge_rules(self, rule_paths: List[str], output_name: str) -> Optional[str]:
        """
        複数のルールをマージして新しいルールを作成

        Args:
            rule_paths: マージするルールファイルのパスリスト
            output_name: 出力ルールの名前

        Returns:
            作成されたルールファイルのパス。エラー時はNone
        """
        try:
            merged_rules = {
                "name": output_name,
                "version": "1.0",
                "description": "マージされたルール",
                "rules": []
            }

            for rule_path in rule_paths:
                rule_data = self.load_rules(rule_path)
                if rule_data and "rules" in rule_data:
                    merged_rules["rules"].extend(rule_data["rules"])

            # 出力パスの生成
            output_filename = f"{output_name.replace(' ', '_')}.json"
            output_path = os.path.join(self.rules_dir, output_filename)

            # 保存
            if self.save_rules(merged_rules, output_path):
                return output_path
            else:
                return None

        except Exception as e:
            print(f"エラー: ルールのマージ中にエラーが発生しました: {e}")
            return None

    def export_rule_template(self, output_path: str) -> bool:
        """
        ルールテンプレートをエクスポート

        Args:
            output_path: 出力先のパス

        Returns:
            成功したらTrue、失敗したらFalse
        """
        template = self.create_default_rule("Template Rule")
        return self.save_rules(template, output_path)
