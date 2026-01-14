"""
メインウィンドウ
アプリケーションのメインGUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from typing import Optional, Dict

# コアモジュール
from core import FileOrganizer, RuleEngine, DuplicateDetector, FolderWatcher
from utils import OperationLogger, BackupManager

# GUIモジュール
from .progress_dialog import ProgressDialog, IndeterminateProgressDialog
from .preview_dialog import PreviewDialog
from .rule_editor import RuleEditorDialog


class MainWindow(tk.Tk):
    """メインウィンドウクラス"""

    def __init__(self):
        super().__init__()

        self.title("File Organizer - ファイル整理ツール")
        self.geometry("900x700")

        # コンポーネントの初期化
        self.organizer = FileOrganizer()
        self.rule_engine = RuleEngine()
        self.backup_manager = BackupManager()
        self.duplicate_detector = DuplicateDetector()
        self.watcher: Optional[FolderWatcher] = None

        # 現在のルールとアクション
        self.current_rules: Optional[Dict] = None
        self.current_actions = []

        # UIの作成
        self._create_menu()
        self._create_widgets()

        # デフォルトルールを読み込み
        self._load_default_rule()

        # ウィンドウを中央に配置
        self.center_window()

    def _create_menu(self) -> None:
        """メニューバーを作成"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # ファイルメニュー
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="ルールを開く", command=self._open_rule)
        file_menu.add_command(label="ルールを保存", command=self._save_rule)
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self.quit)

        # ツールメニュー
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ツール", menu=tools_menu)
        tools_menu.add_command(label="重複ファイル検出", command=self._detect_duplicates)
        tools_menu.add_command(label="バックアップ管理", command=self._manage_backups)
        tools_menu.add_command(label="ログビューア", command=self._view_logs)

        # ヘルプメニュー
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ヘルプ", menu=help_menu)
        help_menu.add_command(label="使い方", command=self._show_help)
        help_menu.add_command(label="バージョン情報", command=self._show_about)

    def _create_widgets(self) -> None:
        """ウィジェットを作成"""
        # メインフレーム
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 上部: ディレクトリ選択
        dir_frame = ttk.LabelFrame(main_frame, text="ディレクトリ選択", padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 10))

        # ソースディレクトリ
        ttk.Label(dir_frame, text="整理元:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_dir_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.source_dir_var, width=50).grid(
            row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 5)
        )
        ttk.Button(dir_frame, text="参照", command=self._browse_source_dir).grid(
            row=0, column=2, pady=5
        )

        # 出力ディレクトリ
        ttk.Label(dir_frame, text="整理先:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=50).grid(
            row=1, column=1, sticky=tk.EW, pady=5, padx=(10, 5)
        )
        ttk.Button(dir_frame, text="参照", command=self._browse_output_dir).grid(
            row=1, column=2, pady=5
        )

        ttk.Checkbutton(
            dir_frame,
            text="同じディレクトリ内で整理（整理先は無視）",
            command=self._toggle_output_dir
        ).grid(row=2, column=1, sticky=tk.W, pady=5)

        dir_frame.columnconfigure(1, weight=1)

        # 中央: ルールとオプション
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 左: ルール情報
        rule_frame = ttk.LabelFrame(middle_frame, text="現在のルール", padding="10")
        rule_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.rule_text = tk.Text(rule_frame, height=10, width=40, wrap=tk.WORD, state='disabled')
        self.rule_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        rule_btn_frame = ttk.Frame(rule_frame)
        rule_btn_frame.pack(fill=tk.X)

        ttk.Button(rule_btn_frame, text="ルール編集", command=self._edit_rule).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(rule_btn_frame, text="デフォルトに戻す", command=self._load_default_rule).pack(
            side=tk.LEFT
        )

        # 右: オプション
        options_frame = ttk.LabelFrame(middle_frame, text="オプション", padding="10")
        options_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # バックアップオプション
        self.backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="整理前にバックアップを作成",
            variable=self.backup_var
        ).pack(anchor=tk.W, pady=5)

        # 操作モード
        ttk.Label(options_frame, text="操作モード:").pack(anchor=tk.W, pady=(10, 5))
        self.operation_mode_var = tk.StringVar(value="move")
        ttk.Radiobutton(
            options_frame,
            text="移動",
            variable=self.operation_mode_var,
            value="move"
        ).pack(anchor=tk.W, padx=(20, 0))
        ttk.Radiobutton(
            options_frame,
            text="コピー",
            variable=self.operation_mode_var,
            value="copy"
        ).pack(anchor=tk.W, padx=(20, 0))

        # 既存ファイル処理
        ttk.Label(options_frame, text="既存ファイル:").pack(anchor=tk.W, pady=(10, 5))
        self.skip_existing_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="スキップする",
            variable=self.skip_existing_var
        ).pack(anchor=tk.W, padx=(20, 0))

        # フォルダ監視
        ttk.Separator(options_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        ttk.Label(options_frame, text="自動整理:").pack(anchor=tk.W, pady=(0, 5))
        self.watch_button = ttk.Button(
            options_frame,
            text="監視開始",
            command=self._toggle_watch
        )
        self.watch_button.pack(fill=tk.X)

        self.watch_status_label = ttk.Label(
            options_frame,
            text="停止中",
            foreground="gray"
        )
        self.watch_status_label.pack(pady=(5, 0))

        # 下部: アクションボタン
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X)

        ttk.Button(
            action_frame,
            text="プレビュー",
            command=self._preview_organization,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            action_frame,
            text="整理実行",
            command=self._execute_organization,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            action_frame,
            text="元に戻す",
            command=self._undo_last_operation,
            width=15
        ).pack(side=tk.LEFT)

        # ステータスバー
        self.status_label = ttk.Label(
            main_frame,
            text="準備完了",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, pady=(10, 0))

    def _browse_source_dir(self) -> None:
        """整理元ディレクトリを選択"""
        directory = filedialog.askdirectory(title="整理元ディレクトリを選択")
        if directory:
            self.source_dir_var.set(directory)

    def _browse_output_dir(self) -> None:
        """整理先ディレクトリを選択"""
        directory = filedialog.askdirectory(title="整理先ディレクトリを選択")
        if directory:
            self.output_dir_var.set(directory)

    def _toggle_output_dir(self) -> None:
        """出力ディレクトリの有効/無効を切り替え"""
        # 実装は簡略化のため省略
        pass

    def _open_rule(self) -> None:
        """ルールファイルを開く"""
        file_path = filedialog.askopenfilename(
            title="ルールファイルを開く",
            filetypes=[("JSONファイル", "*.json"), ("すべてのファイル", "*.*")],
            initialdir="data/rules"
        )

        if file_path:
            rules = self.rule_engine.load_rules(file_path)
            if rules:
                self.current_rules = rules
                self._update_rule_display()
                self.update_status(f"ルールを読み込みました: {file_path}")

    def _save_rule(self) -> None:
        """ルールをファイルに保存"""
        if not self.current_rules:
            messagebox.showwarning("警告", "保存するルールがありません")
            return

        file_path = filedialog.asksaveasfilename(
            title="ルールを保存",
            defaultextension=".json",
            filetypes=[("JSONファイル", "*.json"), ("すべてのファイル", "*.*")],
            initialdir="data/rules"
        )

        if file_path:
            if self.rule_engine.save_rules(self.current_rules, file_path):
                self.update_status(f"ルールを保存しました: {file_path}")

    def _edit_rule(self) -> None:
        """ルールを編集"""
        dialog = RuleEditorDialog(self, self.current_rules)
        self.wait_window(dialog)

        if dialog.result_rules:
            self.current_rules = dialog.result_rules
            self._update_rule_display()
            self.update_status("ルールを更新しました")

    def _load_default_rule(self) -> None:
        """デフォルトルールを読み込み"""
        self.current_rules = self.rule_engine.create_default_rule()
        self._update_rule_display()
        self.update_status("デフォルトルールを読み込みました")

    def _update_rule_display(self) -> None:
        """ルール表示を更新"""
        if not self.current_rules:
            return

        self.rule_text.config(state='normal')
        self.rule_text.delete('1.0', tk.END)

        text = f"ルール名: {self.current_rules.get('name', '不明')}\n\n"
        text += f"説明: {self.current_rules.get('description', 'なし')}\n\n"
        text += "有効なルール:\n"

        for rule in self.current_rules.get('rules', []):
            if rule.get('enabled', True):
                rule_type = rule.get('type', '不明')
                text += f"  - {rule_type}\n"

        self.rule_text.insert('1.0', text)
        self.rule_text.config(state='disabled')

    def _preview_organization(self) -> None:
        """整理のプレビューを表示"""
        source_dir = self.source_dir_var.get()

        if not source_dir or not os.path.exists(source_dir):
            messagebox.showerror("エラー", "有効な整理元ディレクトリを選択してください")
            return

        if not self.current_rules:
            messagebox.showerror("エラー", "ルールが設定されていません")
            return

        # 進捗ダイアログを表示
        progress_dialog = IndeterminateProgressDialog(
            self,
            title="プレビュー生成中",
            message="整理内容を分析しています..."
        )

        def generate_preview():
            try:
                output_dir = self.output_dir_var.get() or source_dir
                actions = self.organizer.organize(
                    source_dir,
                    self.current_rules,
                    output_dir,
                    preview_mode=True,
                    operation_mode=self.operation_mode_var.get()
                )

                self.current_actions = actions

                # メインスレッドでプレビューを表示
                self.after(0, lambda: self._show_preview_dialog(actions, progress_dialog))

            except Exception as e:
                self.after(0, lambda: messagebox.showerror("エラー", f"プレビュー生成中にエラーが発生しました:\n{e}"))
                self.after(0, progress_dialog.close)

        # 別スレッドで実行
        thread = threading.Thread(target=generate_preview, daemon=True)
        thread.start()

    def _show_preview_dialog(self, actions, progress_dialog) -> None:
        """プレビューダイアログを表示"""
        progress_dialog.close()

        if not actions:
            messagebox.showinfo("情報", "整理するファイルがありません")
            return

        # プレビューダイアログを表示
        preview_dialog = PreviewDialog(self, actions)
        self.wait_window(preview_dialog)

        # 確認されたアクションを取得
        confirmed_actions = preview_dialog.get_confirmed_actions()
        if confirmed_actions:
            self.current_actions = confirmed_actions
            # 実行確認
            if messagebox.askyesno("確認", f"{len(confirmed_actions)}件のファイルを整理しますか？"):
                self._execute_with_actions(confirmed_actions)

    def _execute_organization(self) -> None:
        """整理を実行"""
        source_dir = self.source_dir_var.get()

        if not source_dir or not os.path.exists(source_dir):
            messagebox.showerror("エラー", "有効な整理元ディレクトリを選択してください")
            return

        if not self.current_rules:
            messagebox.showerror("エラー", "ルールが設定されていません")
            return

        # 確認
        if not messagebox.askyesno("確認", "ファイルの整理を実行しますか？"):
            return

        # バックアップ作成
        if self.backup_var.get():
            progress_dialog = IndeterminateProgressDialog(
                self,
                title="バックアップ作成中",
                message="整理前のバックアップを作成しています..."
            )

            def create_backup():
                backup_id = self.backup_manager.create_backup(source_dir)
                self.after(0, progress_dialog.close)
                if backup_id:
                    self.update_status(f"バックアップを作成しました: {backup_id}")
                self.after(0, self._execute_organization_worker)

            thread = threading.Thread(target=create_backup, daemon=True)
            thread.start()
        else:
            self._execute_organization_worker()

    def _execute_organization_worker(self) -> None:
        """整理を実行（ワーカー）"""
        source_dir = self.source_dir_var.get()
        output_dir = self.output_dir_var.get() or source_dir

        # アクション生成
        if not self.current_actions:
            self.current_actions = self.organizer.organize(
                source_dir,
                self.current_rules,
                output_dir,
                preview_mode=False,
                operation_mode=self.operation_mode_var.get()
            )

        if not self.current_actions:
            messagebox.showinfo("情報", "整理するファイルがありません")
            return

        self._execute_with_actions(self.current_actions)

    def _execute_with_actions(self, actions) -> None:
        """アクションを実行"""
        # 進捗ダイアログを表示
        progress_dialog = ProgressDialog(
            self,
            title="整理実行中",
            total_items=len(actions)
        )

        def progress_callback(current, total, message):
            self.after(0, lambda: progress_dialog.update_progress(current, message))

        def execute():
            try:
                result = self.organizer.execute_actions(
                    actions,
                    callback=progress_callback,
                    skip_existing=self.skip_existing_var.get()
                )

                # 完了メッセージ
                success_msg = f"整理が完了しました\n\n"
                success_msg += f"成功: {result['successful']}件\n"
                success_msg += f"失敗: {result['failed']}件\n"
                success_msg += f"スキップ: {result['skipped']}件"

                self.after(0, lambda: progress_dialog.complete("完了しました"))
                self.after(0, lambda: messagebox.showinfo("完了", success_msg))
                self.after(0, lambda: self.update_status("整理が完了しました"))

                # アクションをクリア
                self.current_actions = []

            except Exception as e:
                self.after(0, lambda: messagebox.showerror("エラー", f"整理中にエラーが発生しました:\n{e}"))

            finally:
                self.after(0, progress_dialog.destroy)

        # 別スレッドで実行
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()

    def _undo_last_operation(self) -> None:
        """最後の操作を元に戻す"""
        # 最新のログファイルを取得
        logs = self.organizer.logger.list_logs(limit=1)

        if not logs:
            messagebox.showinfo("情報", "元に戻す操作がありません")
            return

        log_file = logs[0]["path"]

        # 確認
        if not messagebox.askyesno("確認", f"最後の操作を元に戻しますか？\n\n操作: {logs[0]['operation_name']}"):
            return

        # 進捗ダイアログを表示
        progress_dialog = IndeterminateProgressDialog(
            self,
            title="元に戻し中",
            message="操作を元に戻しています..."
        )

        def undo():
            try:
                success = self.organizer.undo(log_file)
                self.after(0, progress_dialog.close)

                if success:
                    self.after(0, lambda: messagebox.showinfo("完了", "操作を元に戻しました"))
                    self.after(0, lambda: self.update_status("操作を元に戻しました"))
                else:
                    self.after(0, lambda: messagebox.showerror("エラー", "操作を元に戻せませんでした"))

            except Exception as e:
                self.after(0, progress_dialog.close)
                self.after(0, lambda: messagebox.showerror("エラー", f"エラーが発生しました:\n{e}"))

        thread = threading.Thread(target=undo, daemon=True)
        thread.start()

    def _toggle_watch(self) -> None:
        """フォルダ監視の開始/停止を切り替え"""
        if self.watcher and self.watcher.is_active():
            # 監視停止
            self.watcher.stop_watching()
            self.watcher = None
            self.watch_button.config(text="監視開始")
            self.watch_status_label.config(text="停止中", foreground="gray")
            self.update_status("フォルダ監視を停止しました")
        else:
            # 監視開始
            source_dir = self.source_dir_var.get()

            if not source_dir or not os.path.exists(source_dir):
                messagebox.showerror("エラー", "有効なディレクトリを選択してください")
                return

            if not self.current_rules:
                messagebox.showerror("エラー", "ルールが設定されていません")
                return

            def watch_callback(event_type, file_path):
                self.update_status(f"自動整理: {os.path.basename(file_path)}")

            self.watcher = FolderWatcher(self.organizer)
            if self.watcher.start_watching(source_dir, self.current_rules, watch_callback):
                self.watch_button.config(text="監視停止")
                self.watch_status_label.config(text="監視中", foreground="green")
                self.update_status(f"フォルダ監視を開始しました: {source_dir}")

    def _detect_duplicates(self) -> None:
        """重複ファイルを検出"""
        source_dir = self.source_dir_var.get()

        if not source_dir or not os.path.exists(source_dir):
            messagebox.showerror("エラー", "有効なディレクトリを選択してください")
            return

        messagebox.showinfo("情報", "重複ファイル検出機能は実装中です")

    def _manage_backups(self) -> None:
        """バックアップ管理"""
        messagebox.showinfo("情報", "バックアップ管理機能は実装中です")

    def _view_logs(self) -> None:
        """ログビューア"""
        messagebox.showinfo("情報", "ログビューア機能は実装中です")

    def _show_help(self) -> None:
        """使い方を表示"""
        help_text = """
        File Organizer - ファイル整理ツール

        【基本的な使い方】
        1. 整理元ディレクトリを選択
        2. ルールを編集（必要に応じて）
        3. プレビューで確認
        4. 整理実行

        【機能】
        - 拡張子別分類
        - 日付別分類
        - ファイルサイズ別分類
        - ファイル名パターン分類
        - 自動整理（フォルダ監視）
        - バックアップ作成
        - 元に戻す機能
        """
        messagebox.showinfo("使い方", help_text)

    def _show_about(self) -> None:
        """バージョン情報を表示"""
        about_text = """
        File Organizer
        Version 1.0.0

        フル機能のファイル整理ツール

        (c) 2026
        """
        messagebox.showinfo("バージョン情報", about_text)

    def update_status(self, message: str) -> None:
        """ステータスバーを更新"""
        self.status_label.config(text=message)
        self.update_idletasks()

    def center_window(self) -> None:
        """ウィンドウを画面中央に配置"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
