"""
プレビューダイアログ
整理前のアクションをプレビュー表示
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Optional, Any
import os


class PreviewDialog(tk.Toplevel):
    """整理アクションのプレビューダイアログ"""

    def __init__(self, parent: tk.Widget, actions: List[Dict[str, Any]]):
        """
        Args:
            parent: 親ウィジェット
            actions: プレビューするアクションのリスト
        """
        super().__init__(parent)
        self.title("プレビュー - 整理内容の確認")
        self.actions = actions
        self.filtered_actions = actions.copy()
        self.confirmed = False
        self.selected_actions = []

        # ウィンドウの設定
        self.geometry("900x600")
        self.transient(parent)
        self.grab_set()

        # 中央に配置
        self.center_window()

        # UIの作成
        self._create_widgets()

        # データの表示
        self._populate_tree()

        # 統計情報の更新
        self._update_statistics()

    def _create_widgets(self) -> None:
        """ウィジェットを作成"""
        # メインフレーム
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 上部: タイトルと統計情報
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = ttk.Label(
            top_frame,
            text="以下のファイルが整理されます",
            font=('Arial', 12, 'bold')
        )
        title_label.pack(side=tk.LEFT)

        self.stats_label = ttk.Label(
            top_frame,
            text="",
            font=('Arial', 9)
        )
        self.stats_label.pack(side=tk.RIGHT)

        # フィルターフレーム
        filter_frame = ttk.LabelFrame(main_frame, text="フィルター", padding="5")
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filter_frame, text="検索:").pack(side=tk.LEFT, padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._apply_filter())
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(filter_frame, text="タイプ:").pack(side=tk.LEFT, padx=(0, 5))

        self.type_var = tk.StringVar(value="全て")
        type_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.type_var,
            values=["全て", "move", "copy"],
            state='readonly',
            width=10
        )
        type_combo.pack(side=tk.LEFT)
        type_combo.bind('<<ComboboxSelected>>', lambda e: self._apply_filter())

        # ツリービューフレーム
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # スクロールバー
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # ツリービュー
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('type', 'filename', 'source', 'destination', 'size'),
            show='tree headings',
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            selectmode='extended'
        )

        # 列の設定
        self.tree.column('#0', width=50, minwidth=50)
        self.tree.column('type', width=60, minwidth=60)
        self.tree.column('filename', width=150, minwidth=100)
        self.tree.column('source', width=250, minwidth=150)
        self.tree.column('destination', width=250, minwidth=150)
        self.tree.column('size', width=80, minwidth=60)

        # ヘッダーの設定
        self.tree.heading('#0', text='#')
        self.tree.heading('type', text='タイプ')
        self.tree.heading('filename', text='ファイル名')
        self.tree.heading('source', text='移動元')
        self.tree.heading('destination', text='移動先')
        self.tree.heading('size', text='サイズ')

        self.tree.pack(fill=tk.BOTH, expand=True)

        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        # 下部: ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        # 選択関連ボタン
        select_frame = ttk.Frame(button_frame)
        select_frame.pack(side=tk.LEFT)

        ttk.Button(
            select_frame,
            text="全て選択",
            command=self._select_all
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            select_frame,
            text="全て解除",
            command=self._deselect_all
        ).pack(side=tk.LEFT)

        # 実行/キャンセルボタン
        action_frame = ttk.Frame(button_frame)
        action_frame.pack(side=tk.RIGHT)

        ttk.Button(
            action_frame,
            text="キャンセル",
            command=self._on_cancel
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            action_frame,
            text="実行",
            command=self._on_confirm,
            style='Accent.TButton'
        ).pack(side=tk.LEFT)

    def _populate_tree(self) -> None:
        """ツリービューにデータを表示"""
        # 既存のアイテムをクリア
        for item in self.tree.get_children():
            self.tree.delete(item)

        # アクションを追加
        for i, action in enumerate(self.filtered_actions, 1):
            filename = action.get('filename', os.path.basename(action['source']))
            size_formatted = self._format_size(action.get('size', 0))

            self.tree.insert(
                '',
                'end',
                text=str(i),
                values=(
                    action['type'],
                    filename,
                    action['source'],
                    action['destination'],
                    size_formatted
                ),
                tags=('action',)
            )

    def _apply_filter(self) -> None:
        """フィルターを適用"""
        search_text = self.search_var.get().lower()
        action_type = self.type_var.get()

        # フィルタリング
        self.filtered_actions = []

        for action in self.actions:
            # タイプフィルター
            if action_type != "全て" and action['type'] != action_type:
                continue

            # 検索フィルター
            if search_text:
                filename = action.get('filename', os.path.basename(action['source']))
                source = action['source']
                destination = action['destination']

                if not (search_text in filename.lower() or
                       search_text in source.lower() or
                       search_text in destination.lower()):
                    continue

            self.filtered_actions.append(action)

        # ツリービューを更新
        self._populate_tree()
        self._update_statistics()

    def _update_statistics(self) -> None:
        """統計情報を更新"""
        total = len(self.filtered_actions)
        total_size = sum(action.get('size', 0) for action in self.filtered_actions)

        stats_text = f"表示中: {total}件 / 合計: {len(self.actions)}件 | サイズ: {self._format_size(total_size)}"
        self.stats_label.config(text=stats_text)

    def _select_all(self) -> None:
        """すべてのアイテムを選択"""
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    def _deselect_all(self) -> None:
        """すべての選択を解除"""
        self.tree.selection_remove(self.tree.selection())

    def _on_confirm(self) -> None:
        """実行ボタンが押された時の処理"""
        # 選択されたアイテムを取得
        selected_items = self.tree.selection()

        if not selected_items:
            # 何も選択されていない場合は全て実行
            self.selected_actions = self.filtered_actions
        else:
            # 選択されたアイテムのみ実行
            self.selected_actions = []
            for item in selected_items:
                index = int(self.tree.item(item, 'text')) - 1
                if 0 <= index < len(self.filtered_actions):
                    self.selected_actions.append(self.filtered_actions[index])

        self.confirmed = True
        self.destroy()

    def _on_cancel(self) -> None:
        """キャンセルボタンが押された時の処理"""
        self.confirmed = False
        self.destroy()

    def get_confirmed_actions(self) -> Optional[List[Dict[str, Any]]]:
        """
        確認されたアクションのリストを取得

        Returns:
            確認された場合はアクションリスト、キャンセルされた場合はNone
        """
        if self.confirmed:
            return self.selected_actions
        return None

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """
        バイト数を人間が読みやすい形式に変換
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def center_window(self) -> None:
        """ウィンドウを画面中央に配置"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
