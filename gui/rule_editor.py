"""
ルール編集ダイアログ
整理ルールをGUIで作成・編集
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Optional, List
import json


class RuleEditorDialog(tk.Toplevel):
    """ルールを編集するダイアログ"""

    def __init__(self, parent: tk.Widget, existing_rules: Optional[Dict] = None):
        """
        Args:
            parent: 親ウィジェット
            existing_rules: 既存のルール（編集時）
        """
        super().__init__(parent)
        self.title("ルール編集")
        self.existing_rules = existing_rules
        self.result_rules = None

        # ウィンドウの設定
        self.geometry("700x750")
        self.transient(parent)
        self.grab_set()

        # 中央に配置
        self.center_window()

        # UIの作成
        self._create_widgets()

        # 既存のルールがあれば読み込み
        if existing_rules:
            self._load_existing_rules()

    def _create_widgets(self) -> None:
        """ウィジェットを作成"""
        # メインフレーム
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 上部: 基本情報
        info_frame = ttk.LabelFrame(main_frame, text="基本情報", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))

        # ルール名
        ttk.Label(info_frame, text="ルール名:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value="新規ルール")
        ttk.Entry(info_frame, textvariable=self.name_var, width=40).grid(
            row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 0)
        )

        # 説明
        ttk.Label(info_frame, text="説明:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.desc_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.desc_var, width=40).grid(
            row=1, column=1, sticky=tk.EW, pady=5, padx=(10, 0)
        )

        info_frame.columnconfigure(1, weight=1)

        # タブノートブック
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 各ルールタイプのタブを作成
        self._create_extension_tab()
        self._create_date_tab()
        self._create_size_tab()
        self._create_pattern_tab()

        # 下部: ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(
            button_frame,
            text="キャンセル",
            command=self._on_cancel
        ).pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Button(
            button_frame,
            text="保存",
            command=self._on_save
        ).pack(side=tk.RIGHT)

        ttk.Button(
            button_frame,
            text="テンプレート読み込み",
            command=self._load_template
        ).pack(side=tk.LEFT)

    def _create_extension_tab(self) -> None:
        """拡張子別分類タブを作成"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="拡張子分類")

        # 有効/無効
        self.ext_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            tab,
            text="拡張子による分類を有効にする",
            variable=self.ext_enabled_var
        ).pack(anchor=tk.W, pady=(0, 10))

        # カテゴリリスト
        list_frame = ttk.Frame(tab)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # リストボックス
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.ext_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=15)
        self.ext_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.ext_listbox.yview)

        # ボタン
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="追加", command=self._add_extension_category).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="編集", command=self._edit_extension_category).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="削除", command=self._delete_extension_category).pack(side=tk.LEFT)

        # デフォルトカテゴリを追加
        self.ext_categories = {}
        self._load_default_categories()

    def _create_date_tab(self) -> None:
        """日付別分類タブを作成"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="日付分類")

        # 有効/無効
        self.date_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            tab,
            text="日付による分類を有効にする",
            variable=self.date_enabled_var
        ).pack(anchor=tk.W, pady=(0, 10))

        # 設定フレーム
        settings_frame = ttk.LabelFrame(tab, text="設定", padding="10")
        settings_frame.pack(fill=tk.X)

        # モード選択
        ttk.Label(settings_frame, text="基準日付:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.date_mode_var = tk.StringVar(value="modified")
        mode_frame = ttk.Frame(settings_frame)
        mode_frame.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        ttk.Radiobutton(
            mode_frame,
            text="更新日",
            variable=self.date_mode_var,
            value="modified"
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            mode_frame,
            text="作成日",
            variable=self.date_mode_var,
            value="created"
        ).pack(side=tk.LEFT)

        # フォーマット選択
        ttk.Label(settings_frame, text="フォルダ形式:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.date_format_var = tk.StringVar(value="%Y/%m")
        format_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.date_format_var,
            values=["%Y/%m", "%Y/%m/%d", "%Y", "%Y-%m", "%Y-%m-%d"],
            width=20
        )
        format_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # 例の表示
        example_frame = ttk.Frame(settings_frame)
        example_frame.grid(row=2, column=1, sticky=tk.W, pady=10, padx=(10, 0))
        ttk.Label(example_frame, text="例:", font=('Arial', 9)).pack(side=tk.LEFT)
        ttk.Label(
            example_frame,
            text="2026/01 (年/月)",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        ).pack(side=tk.LEFT, padx=(5, 0))

    def _create_size_tab(self) -> None:
        """サイズ別分類タブを作成"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="サイズ分類")

        # 有効/無効
        self.size_enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            tab,
            text="サイズによる分類を有効にする",
            variable=self.size_enabled_var
        ).pack(anchor=tk.W, pady=(0, 10))

        # 閾値設定
        settings_frame = ttk.LabelFrame(tab, text="サイズ閾値", padding="10")
        settings_frame.pack(fill=tk.X)

        # Small
        ttk.Label(settings_frame, text="Small (小):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.size_small_var = tk.StringVar(value="1")
        size_small_frame = ttk.Frame(settings_frame)
        size_small_frame.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        ttk.Entry(size_small_frame, textvariable=self.size_small_var, width=10).pack(side=tk.LEFT)
        ttk.Label(size_small_frame, text="MB 以下").pack(side=tk.LEFT, padx=(5, 0))

        # Medium
        ttk.Label(settings_frame, text="Medium (中):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.size_medium_var = tk.StringVar(value="100")
        size_medium_frame = ttk.Frame(settings_frame)
        size_medium_frame.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        ttk.Entry(size_medium_frame, textvariable=self.size_medium_var, width=10).pack(side=tk.LEFT)
        ttk.Label(size_medium_frame, text="MB 以下").pack(side=tk.LEFT, padx=(5, 0))

        # Large
        ttk.Label(settings_frame, text="Large (大):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.size_large_var = tk.StringVar(value="1024")
        size_large_frame = ttk.Frame(settings_frame)
        size_large_frame.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        ttk.Entry(size_large_frame, textvariable=self.size_large_var, width=10).pack(side=tk.LEFT)
        ttk.Label(size_large_frame, text="MB 以下").pack(side=tk.LEFT, padx=(5, 0))

        ttk.Label(
            settings_frame,
            text="※ これらを超えるものはVeryLarge（特大）に分類されます",
            font=('Arial', 8),
            foreground='gray'
        ).grid(row=3, column=1, sticky=tk.W, pady=(10, 0), padx=(10, 0))

    def _create_pattern_tab(self) -> None:
        """パターン分類タブを作成"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="パターン分類")

        # 有効/無効
        self.pattern_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            tab,
            text="ファイル名パターンによる分類を有効にする",
            variable=self.pattern_enabled_var
        ).pack(anchor=tk.W, pady=(0, 10))

        # パターンリスト
        list_frame = ttk.Frame(tab)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # リストボックス
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.pattern_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=15)
        self.pattern_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.pattern_listbox.yview)

        # ボタン
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="追加", command=self._add_pattern).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="編集", command=self._edit_pattern).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="削除", command=self._delete_pattern).pack(side=tk.LEFT)

        # デフォルトパターンを追加
        self.patterns = {}
        self._load_default_patterns()

    def _load_default_categories(self) -> None:
        """デフォルトカテゴリを読み込み"""
        default_categories = {
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
            "Videos": [".mp4", ".avi", ".mkv", ".mov"],
            "Documents": [".pdf", ".doc", ".docx", ".txt"],
            "Audio": [".mp3", ".wav", ".flac", ".aac"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"]
        }

        for category, extensions in default_categories.items():
            self.ext_categories[category] = extensions
            self.ext_listbox.insert(tk.END, f"{category}: {', '.join(extensions)}")

    def _load_default_patterns(self) -> None:
        """デフォルトパターンを読み込み"""
        default_patterns = {
            "Screenshots": "^screenshot[_-].*",
            "Camera": "^(IMG|DSC|DCIM)[_-].*"
        }

        for category, pattern in default_patterns.items():
            self.patterns[category] = pattern
            self.pattern_listbox.insert(tk.END, f"{category}: {pattern}")

    def _add_extension_category(self) -> None:
        """拡張子カテゴリを追加"""
        dialog = CategoryDialog(self, "拡張子カテゴリの追加")
        self.wait_window(dialog)

        if dialog.result:
            category, extensions = dialog.result
            self.ext_categories[category] = extensions
            self.ext_listbox.insert(tk.END, f"{category}: {', '.join(extensions)}")

    def _edit_extension_category(self) -> None:
        """拡張子カテゴリを編集"""
        selection = self.ext_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "編集するカテゴリを選択してください")
            return

        index = selection[0]
        category_name = list(self.ext_categories.keys())[index]
        extensions = self.ext_categories[category_name]

        dialog = CategoryDialog(self, "拡張子カテゴリの編集", category_name, extensions)
        self.wait_window(dialog)

        if dialog.result:
            new_category, new_extensions = dialog.result
            del self.ext_categories[category_name]
            self.ext_categories[new_category] = new_extensions
            self.ext_listbox.delete(index)
            self.ext_listbox.insert(index, f"{new_category}: {', '.join(new_extensions)}")

    def _delete_extension_category(self) -> None:
        """拡張子カテゴリを削除"""
        selection = self.ext_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "削除するカテゴリを選択してください")
            return

        index = selection[0]
        category_name = list(self.ext_categories.keys())[index]
        del self.ext_categories[category_name]
        self.ext_listbox.delete(index)

    def _add_pattern(self) -> None:
        """パターンを追加"""
        dialog = PatternDialog(self, "パターンの追加")
        self.wait_window(dialog)

        if dialog.result:
            category, pattern = dialog.result
            self.patterns[category] = pattern
            self.pattern_listbox.insert(tk.END, f"{category}: {pattern}")

    def _edit_pattern(self) -> None:
        """パターンを編集"""
        selection = self.pattern_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "編集するパターンを選択してください")
            return

        index = selection[0]
        category_name = list(self.patterns.keys())[index]
        pattern = self.patterns[category_name]

        dialog = PatternDialog(self, "パターンの編集", category_name, pattern)
        self.wait_window(dialog)

        if dialog.result:
            new_category, new_pattern = dialog.result
            del self.patterns[category_name]
            self.patterns[new_category] = new_pattern
            self.pattern_listbox.delete(index)
            self.pattern_listbox.insert(index, f"{new_category}: {new_pattern}")

    def _delete_pattern(self) -> None:
        """パターンを削除"""
        selection = self.pattern_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "削除するパターンを選択してください")
            return

        index = selection[0]
        category_name = list(self.patterns.keys())[index]
        del self.patterns[category_name]
        self.pattern_listbox.delete(index)

    def _load_template(self) -> None:
        """テンプレートを読み込み"""
        file_path = filedialog.askopenfilename(
            title="テンプレートを開く",
            filetypes=[("JSONファイル", "*.json"), ("すべてのファイル", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    rules = json.load(f)
                self._load_existing_rules(rules)
                messagebox.showinfo("成功", "テンプレートを読み込みました")
            except Exception as e:
                messagebox.showerror("エラー", f"テンプレートの読み込みに失敗しました:\n{e}")

    def _load_existing_rules(self, rules: Optional[Dict] = None) -> None:
        """既存のルールを読み込み"""
        if rules is None:
            rules = self.existing_rules

        if not rules:
            return

        # 基本情報
        self.name_var.set(rules.get("name", ""))
        self.desc_var.set(rules.get("description", ""))

        # 各ルールを読み込み
        for rule in rules.get("rules", []):
            rule_type = rule.get("type")

            if rule_type == "extension" and "categories" in rule:
                self.ext_enabled_var.set(rule.get("enabled", True))
                self.ext_categories = rule["categories"]
                self.ext_listbox.delete(0, tk.END)
                for category, extensions in self.ext_categories.items():
                    self.ext_listbox.insert(tk.END, f"{category}: {', '.join(extensions)}")

            elif rule_type == "date":
                self.date_enabled_var.set(rule.get("enabled", True))
                self.date_mode_var.set(rule.get("mode", "modified"))
                self.date_format_var.set(rule.get("format", "%Y/%m"))

            elif rule_type == "size" and "thresholds" in rule:
                self.size_enabled_var.set(rule.get("enabled", True))
                thresholds = rule["thresholds"]
                if "Small" in thresholds:
                    self.size_small_var.set(str(thresholds["Small"] // (1024 * 1024)))
                if "Medium" in thresholds:
                    self.size_medium_var.set(str(thresholds["Medium"] // (1024 * 1024)))
                if "Large" in thresholds:
                    self.size_large_var.set(str(thresholds["Large"] // (1024 * 1024)))

            elif rule_type == "pattern" and "patterns" in rule:
                self.pattern_enabled_var.set(rule.get("enabled", True))
                self.patterns = rule["patterns"]
                self.pattern_listbox.delete(0, tk.END)
                for category, pattern in self.patterns.items():
                    self.pattern_listbox.insert(tk.END, f"{category}: {pattern}")

    def _on_save(self) -> None:
        """保存ボタンが押された時の処理"""
        # ルールを構築
        rules = {
            "name": self.name_var.get() or "新規ルール",
            "version": "1.0",
            "description": self.desc_var.get(),
            "priority": ["pattern", "extension", "date", "size"],
            "rules": []
        }

        # 拡張子ルール
        if self.ext_enabled_var.get() and self.ext_categories:
            rules["rules"].append({
                "type": "extension",
                "enabled": True,
                "categories": self.ext_categories
            })

        # 日付ルール
        if self.date_enabled_var.get():
            rules["rules"].append({
                "type": "date",
                "enabled": True,
                "mode": self.date_mode_var.get(),
                "format": self.date_format_var.get()
            })

        # サイズルール
        if self.size_enabled_var.get():
            try:
                rules["rules"].append({
                    "type": "size",
                    "enabled": True,
                    "thresholds": {
                        "Small": int(float(self.size_small_var.get()) * 1024 * 1024),
                        "Medium": int(float(self.size_medium_var.get()) * 1024 * 1024),
                        "Large": int(float(self.size_large_var.get()) * 1024 * 1024)
                    }
                })
            except ValueError:
                messagebox.showerror("エラー", "サイズの値が不正です")
                return

        # パターンルール
        if self.pattern_enabled_var.get() and self.patterns:
            rules["rules"].append({
                "type": "pattern",
                "enabled": True,
                "patterns": self.patterns
            })

        self.result_rules = rules
        self.destroy()

    def _on_cancel(self) -> None:
        """キャンセルボタンが押された時の処理"""
        self.result_rules = None
        self.destroy()

    def center_window(self) -> None:
        """ウィンドウを画面中央に配置"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')


class CategoryDialog(tk.Toplevel):
    """カテゴリ追加/編集ダイアログ"""

    def __init__(self, parent: tk.Widget, title: str,
                 category: str = "", extensions: List[str] = None):
        super().__init__(parent)
        self.title(title)
        self.result = None

        self.geometry("400x200")
        self.transient(parent)
        self.grab_set()

        # UI作成
        frame = ttk.Frame(self, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="カテゴリ名:").pack(anchor=tk.W, pady=(0, 5))
        self.category_var = tk.StringVar(value=category)
        ttk.Entry(frame, textvariable=self.category_var, width=40).pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, text="拡張子 (カンマ区切り):").pack(anchor=tk.W, pady=(0, 5))
        self.extensions_var = tk.StringVar(value=", ".join(extensions) if extensions else "")
        ttk.Entry(frame, textvariable=self.extensions_var, width=40).pack(fill=tk.X, pady=(0, 20))

        button_frame = ttk.Frame(frame)
        button_frame.pack()

        ttk.Button(button_frame, text="OK", command=self._on_ok).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="キャンセル", command=self.destroy).pack(side=tk.LEFT)

    def _on_ok(self) -> None:
        category = self.category_var.get().strip()
        extensions_str = self.extensions_var.get().strip()

        if not category:
            messagebox.showwarning("警告", "カテゴリ名を入力してください")
            return

        if not extensions_str:
            messagebox.showwarning("警告", "拡張子を入力してください")
            return

        extensions = [ext.strip() for ext in extensions_str.split(",")]
        extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]

        self.result = (category, extensions)
        self.destroy()


class PatternDialog(tk.Toplevel):
    """パターン追加/編集ダイアログ"""

    def __init__(self, parent: tk.Widget, title: str,
                 category: str = "", pattern: str = ""):
        super().__init__(parent)
        self.title(title)
        self.result = None

        self.geometry("400x200")
        self.transient(parent)
        self.grab_set()

        # UI作成
        frame = ttk.Frame(self, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="カテゴリ名:").pack(anchor=tk.W, pady=(0, 5))
        self.category_var = tk.StringVar(value=category)
        ttk.Entry(frame, textvariable=self.category_var, width=40).pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, text="正規表現パターン:").pack(anchor=tk.W, pady=(0, 5))
        self.pattern_var = tk.StringVar(value=pattern)
        ttk.Entry(frame, textvariable=self.pattern_var, width=40).pack(fill=tk.X, pady=(0, 20))

        button_frame = ttk.Frame(frame)
        button_frame.pack()

        ttk.Button(button_frame, text="OK", command=self._on_ok).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="キャンセル", command=self.destroy).pack(side=tk.LEFT)

    def _on_ok(self) -> None:
        category = self.category_var.get().strip()
        pattern = self.pattern_var.get().strip()

        if not category:
            messagebox.showwarning("警告", "カテゴリ名を入力してください")
            return

        if not pattern:
            messagebox.showwarning("警告", "パターンを入力してください")
            return

        self.result = (category, pattern)
        self.destroy()
