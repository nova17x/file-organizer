"""
進捗表示ダイアログ
ファイル整理の進捗状況を表示
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional


class ProgressDialog(tk.Toplevel):
    """進捗状況を表示するダイアログ"""

    def __init__(self, parent: tk.Widget, title: str = "処理中",
                 total_items: int = 100, cancelable: bool = True):
        """
        Args:
            parent: 親ウィジェット
            title: ダイアログのタイトル
            total_items: 処理する総アイテム数
            cancelable: キャンセル可能かどうか
        """
        super().__init__(parent)
        self.title(title)
        self.total_items = total_items
        self.current_item = 0
        self.is_cancelled = False
        self.cancelable = cancelable

        # ウィンドウの設定
        self.geometry("500x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # 中央に配置
        self.center_window()

        # UIの作成
        self._create_widgets()

        # 閉じるボタンを無効化
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_widgets(self) -> None:
        """ウィジェットを作成"""
        # メインフレーム
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # タイトルラベル
        self.title_label = ttk.Label(
            main_frame,
            text="処理を実行中...",
            font=('Arial', 12, 'bold')
        )
        self.title_label.pack(pady=(0, 10))

        # ステータスラベル
        self.status_label = ttk.Label(
            main_frame,
            text="準備中...",
            font=('Arial', 10)
        )
        self.status_label.pack(pady=(0, 10))

        # プログレスバー
        self.progress_bar = ttk.Progressbar(
            main_frame,
            mode='determinate',
            length=400,
            maximum=self.total_items
        )
        self.progress_bar.pack(pady=(0, 10))

        # 進捗テキスト（例: 50/100）
        self.progress_text = ttk.Label(
            main_frame,
            text=f"0 / {self.total_items}",
            font=('Arial', 9)
        )
        self.progress_text.pack(pady=(0, 20))

        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()

        # キャンセルボタン
        if self.cancelable:
            self.cancel_button = ttk.Button(
                button_frame,
                text="キャンセル",
                command=self._on_cancel
            )
            self.cancel_button.pack()

    def update_progress(self, current: int, message: str = "") -> None:
        """
        進捗を更新

        Args:
            current: 現在の進捗（処理したアイテム数）
            message: 表示するメッセージ
        """
        self.current_item = current

        # プログレスバーを更新
        self.progress_bar['value'] = current

        # 進捗テキストを更新
        percentage = (current / self.total_items * 100) if self.total_items > 0 else 0
        self.progress_text.config(
            text=f"{current} / {self.total_items} ({percentage:.1f}%)"
        )

        # メッセージを更新
        if message:
            self.status_label.config(text=message)

        # UIを更新
        self.update_idletasks()

    def set_status(self, status_text: str) -> None:
        """
        ステータステキストを設定

        Args:
            status_text: 表示するステータス
        """
        self.status_label.config(text=status_text)
        self.update_idletasks()

    def set_title(self, title_text: str) -> None:
        """
        タイトルテキストを設定

        Args:
            title_text: 表示するタイトル
        """
        self.title_label.config(text=title_text)
        self.update_idletasks()

    def complete(self, message: str = "完了しました") -> None:
        """
        処理完了を表示

        Args:
            message: 完了メッセージ
        """
        self.progress_bar['value'] = self.total_items
        self.status_label.config(text=message)

        if self.cancelable:
            self.cancel_button.config(text="閉じる", command=self.destroy)

        self.update_idletasks()

    def cancel_operation(self) -> None:
        """操作をキャンセル"""
        self.is_cancelled = True

    def _on_cancel(self) -> None:
        """キャンセルボタンが押された時の処理"""
        self.is_cancelled = True
        self.cancel_button.config(state='disabled')
        self.status_label.config(text="キャンセル中...")
        self.update_idletasks()

    def _on_close(self) -> None:
        """ウィンドウを閉じようとした時の処理"""
        if self.cancelable:
            self._on_cancel()

    def center_window(self) -> None:
        """ウィンドウを画面中央に配置"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')


class IndeterminateProgressDialog(tk.Toplevel):
    """不定進捗を表示するダイアログ（処理数が不明な場合）"""

    def __init__(self, parent: tk.Widget, title: str = "処理中",
                 message: str = "処理を実行中..."):
        """
        Args:
            parent: 親ウィジェット
            title: ダイアログのタイトル
            message: 表示するメッセージ
        """
        super().__init__(parent)
        self.title(title)

        # ウィンドウの設定
        self.geometry("400x150")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # UIの作成
        self._create_widgets(message)

        # 中央に配置
        self.center_window()

        # 閉じるボタンを無効化
        self.protocol("WM_DELETE_WINDOW", lambda: None)

    def _create_widgets(self, message: str) -> None:
        """ウィジェットを作成"""
        # メインフレーム
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # メッセージラベル
        self.message_label = ttk.Label(
            main_frame,
            text=message,
            font=('Arial', 10)
        )
        self.message_label.pack(pady=(0, 20))

        # 不定プログレスバー
        self.progress_bar = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=300
        )
        self.progress_bar.pack()
        self.progress_bar.start(10)  # アニメーション開始

    def set_message(self, message: str) -> None:
        """
        メッセージを更新

        Args:
            message: 表示するメッセージ
        """
        self.message_label.config(text=message)
        self.update_idletasks()

    def center_window(self) -> None:
        """ウィンドウを画面中央に配置"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def close(self) -> None:
        """ダイアログを閉じる"""
        self.progress_bar.stop()
        self.destroy()
