# File Organizer - ファイル整理ツール

フル機能のファイル整理アプリケーション。散らかったファイルを自動的に整理し、管理しやすくします。

## 特徴

### 分類機能
- **拡張子別分類**: 画像、動画、ドキュメント、音楽などのカテゴリに自動分類
- **日付別分類**: 作成日・更新日で年月フォルダに自動分類
- **ファイルサイズ別分類**: 大きいファイルを別フォルダへ分類
- **ファイル名パターン分類**: screenshot_*, IMG_* などのパターンで分類

### 便利機能
- **重複ファイル検出**: ハッシュ値でファイルを比較し重複を検出
- **プレビュー機能**: 移動前に確認できる安全設計
- **ルール保存・読み込み**: JSON形式でルールを保存・再利用
- **フォルダ監視モード**: ファイル作成時に自動で整理

### 安全機能
- **バックアップ作成**: 整理前の状態を自動保存
- **ログ記録**: 何をどこに移動したか完全記録
- **元に戻す機能**: ログから簡単に復元可能

### GUI機能
- **Tkinterベースの直感的UI**: 使いやすいグラフィカルインターフェース
- **ドラッグ&ドロップ対応**: ファイルやフォルダを簡単に選択
- **進捗表示**: プログレスバーで処理状況を可視化
- **カスタムルール設定画面**: 柔軟なルール作成が可能

## インストール

### 必要要件
- Python 3.8 以上

### セットアップ

1. リポジトリをクローン
```bash
git clone <repository-url>
cd file-organizer
```

2. 依存パッケージをインストール
```bash
pip install -r requirements.txt
```

## 使い方

### GUIモードで起動

```bash
python main.py
```

### 基本的な使い方

1. **整理元ディレクトリを選択**
   - 「参照」ボタンをクリックして整理したいフォルダを選択

2. **ルールを設定**（オプション）
   - 「ルール編集」ボタンでカスタムルールを作成
   - または既存のルールファイルを読み込み

3. **プレビューで確認**
   - 「プレビュー」ボタンで整理内容を事前確認
   - フィルタ機能で特定のファイルのみ表示可能

4. **整理を実行**
   - 「整理実行」ボタンでファイルを整理
   - バックアップが自動的に作成されます

### 自動整理（フォルダ監視）

1. 整理元ディレクトリとルールを設定
2. 「監視開始」ボタンをクリック
3. フォルダに新しいファイルが追加されると自動的に整理されます

### 元に戻す

1. 「元に戻す」ボタンをクリック
2. 最後の操作が取り消され、ファイルが元の場所に戻ります

## プロジェクト構造

```
file-organizer/
├── main.py                    # エントリーポイント
├── requirements.txt           # 依存パッケージ
├── config/
│   ├── __init__.py
│   └── settings.py           # 設定ファイル
├── core/
│   ├── __init__.py
│   ├── classifier.py         # ファイル分類エンジン
│   ├── file_manager.py       # ファイル操作管理
│   ├── duplicate_detector.py # 重複検出
│   ├── rule_engine.py        # ルール処理
│   └── watcher.py            # フォルダ監視
├── utils/
│   ├── __init__.py
│   ├── logger.py             # ログ記録
│   ├── backup.py             # バックアップ管理
│   └── hash_utils.py         # ハッシュ計算
├── gui/
│   ├── __init__.py
│   ├── main_window.py        # メインウィンドウ
│   ├── rule_editor.py        # ルール設定画面
│   ├── preview_dialog.py     # プレビュー画面
│   └── progress_dialog.py    # 進捗表示
└── data/
    ├── rules/                # 保存されたルール
    ├── logs/                 # ログファイル
    └── backups/              # バックアップデータ
```

## ルールのカスタマイズ

### ルールファイルの形式（JSON）

```json
{
  "name": "My Organize Rule",
  "version": "1.0",
  "description": "カスタム整理ルール",
  "priority": ["pattern", "extension", "date"],
  "rules": [
    {
      "type": "extension",
      "enabled": true,
      "categories": {
        "Images": [".jpg", ".png", ".gif"],
        "Documents": [".pdf", ".docx", ".txt"]
      }
    },
    {
      "type": "date",
      "enabled": true,
      "mode": "modified",
      "format": "%Y/%m"
    },
    {
      "type": "size",
      "enabled": false,
      "thresholds": {
        "Small": 1048576,
        "Medium": 104857600,
        "Large": 1073741824
      }
    },
    {
      "type": "pattern",
      "enabled": true,
      "patterns": {
        "Screenshots": "^screenshot_.*",
        "Camera": "^IMG_.*"
      }
    }
  ]
}
```

### ルールタイプ

#### 1. 拡張子による分類 (extension)
ファイルの拡張子に基づいてカテゴリに分類します。

```json
{
  "type": "extension",
  "enabled": true,
  "categories": {
    "カテゴリ名": [".拡張子1", ".拡張子2"]
  }
}
```

#### 2. 日付による分類 (date)
ファイルの作成日または更新日に基づいて分類します。

```json
{
  "type": "date",
  "enabled": true,
  "mode": "modified",  // "created" または "modified"
  "format": "%Y/%m"    // 日付フォーマット
}
```

日付フォーマット例:
- `%Y/%m` → 2026/01
- `%Y/%m/%d` → 2026/01/14
- `%Y` → 2026

#### 3. サイズによる分類 (size)
ファイルサイズに基づいて分類します。

```json
{
  "type": "size",
  "enabled": true,
  "thresholds": {
    "Small": 1048576,      // 1MB
    "Medium": 104857600,   // 100MB
    "Large": 1073741824    // 1GB
  }
}
```

#### 4. パターンによる分類 (pattern)
ファイル名のパターンマッチングで分類します（正規表現対応）。

```json
{
  "type": "pattern",
  "enabled": true,
  "patterns": {
    "Screenshots": "^screenshot[_-].*",
    "Camera": "^(IMG|DSC)[_-].*"
  }
}
```

### 優先順位

`priority` フィールドでルールの適用順序を指定できます。

```json
"priority": ["pattern", "extension", "date", "size"]
```

先に指定されたルールが優先されます。

## コマンドラインから使用する（上級者向け）

Pythonスクリプトとして直接使用することも可能です。

```python
from core import FileOrganizer, RuleEngine

# オーガナイザーを作成
organizer = FileOrganizer()

# ルールを読み込み
rule_engine = RuleEngine()
rules = rule_engine.load_rules("data/rules/my_rule.json")

# 整理を実行
actions = organizer.organize("/path/to/source", rules)
result = organizer.execute_actions(actions)

print(f"成功: {result['successful']}件")
```

## トラブルシューティング

### tkinterdnd2のインストールエラー

tkinterdnd2が正しくインストールできない場合:

```bash
pip install --upgrade tkinterdnd2
```

それでも動作しない場合は、ドラッグ&ドロップ機能なしでも使用できます。

### 監視が動作しない

watchdogライブラリが正しくインストールされているか確認してください:

```bash
pip install --upgrade watchdog
```

### バックアップが作成されない

`data/backups/` ディレクトリへの書き込み権限があるか確認してください。

## よくある質問

**Q: 整理前にファイルを確認できますか？**
A: はい、「プレビュー」ボタンで整理内容を事前に確認できます。

**Q: 間違えて整理してしまった場合は？**
A: 「元に戻す」ボタンで最後の操作を取り消せます。

**Q: 複数のルールを同時に適用できますか？**
A: はい、ルールエディタで複数のルールタイプを組み合わせられます。

**Q: 大量のファイルを処理できますか？**
A: はい、プログレスバーで進捗を確認しながら処理できます。

**Q: ネットワークドライブでも使用できますか？**
A: はい、ただしネットワークの速度により処理時間が長くなる場合があります。

## ライセンス

MIT License

## 貢献

バグ報告や機能リクエストは Issue でお願いします。

## 注意事項

- 重要なファイルを整理する前に必ずバックアップを取ることをお勧めします
- 元に戻す機能はログに基づいているため、ログファイルを削除すると使用できません
- 大量のファイルを処理する場合は時間がかかることがあります

---

**File Organizer** - あなたのファイル整理を簡単に
