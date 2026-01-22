"""
メインウィンドウ (PyQt6版)
アプリケーションのメインGUI
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QRadioButton,
    QTextEdit, QGroupBox, QFileDialog, QMessageBox, QButtonGroup
)
from PyQt6.QtCore import Qt, QTimer
from typing import Optional, Dict

# コアモジュール
from core import FileOrganizer, RuleEngine, DuplicateDetector, FolderWatcher
from utils import OperationLogger, BackupManager

# GUIモジュール
from .qt_progress_dialog import ProgressDialog, IndeterminateProgressDialog
from .qt_preview_dialog import PreviewDialog
from .qt_rule_editor import RuleEditorDialog
from .qt_workers import OrganizeWorker, ExecuteWorker, UndoWorker, BackupWorker
from .themes import ThemeManager, ThemeType


class QtMainWindow(QMainWindow):
    """メインウィンドウクラス"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Organizer - ファイル整理ツール")
        self.resize(900, 700)

        # コンポーネントの初期化
        self.organizer = FileOrganizer()
        self.rule_engine = RuleEngine()
        self.backup_manager = BackupManager()
        self.duplicate_detector = DuplicateDetector()
        self.watcher: Optional[FolderWatcher] = None

        # 現在のルールとアクション
        self.current_rules: Optional[Dict] = None
        self.current_actions = []

        # ワーカーとダイアログの参照
        self.current_worker = None
        self.current_progress_dialog = None
        self.cancel_timer = None

        # UIの作成
        self._create_menu()
        self._create_widgets()

        # デフォルトルールを読み込み
        self._load_default_rule()

        # ウィンドウを中央に配置
        self.center_on_screen()

    def center_on_screen(self):
        """ウィンドウを画面中央に配置"""
        screen_geometry = self.screen().geometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def _create_menu(self) -> None:
        """メニューバーを作成"""
        menubar = self.menuBar()

        # ファイルメニュー
        file_menu = menubar.addMenu("ファイル")
        file_menu.addAction("ルールを開く", self._open_rule)
        file_menu.addAction("ルールを保存", self._save_rule)
        file_menu.addSeparator()
        file_menu.addAction("終了", self.close)

        # ツールメニュー
        tools_menu = menubar.addMenu("ツール")
        tools_menu.addAction("重複ファイル検出", self._detect_duplicates)
        tools_menu.addAction("バックアップ管理", self._manage_backups)
        tools_menu.addAction("ログビューア", self._view_logs)

        # 設定メニュー
        settings_menu = menubar.addMenu("設定")
        self.theme_action_dark = settings_menu.addAction("ダークテーマ", lambda: self._change_theme(ThemeType.DARK))
        self.theme_action_light = settings_menu.addAction("ライトテーマ", lambda: self._change_theme(ThemeType.LIGHT))

        # ヘルプメニュー
        help_menu = menubar.addMenu("ヘルプ")
        help_menu.addAction("使い方", self._show_help)
        help_menu.addAction("バージョン情報", self._show_about)

    def _create_widgets(self) -> None:
        """ウィジェットを作成"""
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # メインレイアウト
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # ディレクトリ選択セクション
        dir_group = QGroupBox("ディレクトリ選択")
        dir_layout = QGridLayout()

        # 整理元
        dir_layout.addWidget(QLabel("整理元:"), 0, 0)
        self.source_dir_edit = QLineEdit()
        dir_layout.addWidget(self.source_dir_edit, 0, 1)
        browse_source_btn = QPushButton("参照")
        browse_source_btn.clicked.connect(self._browse_source_dir)
        dir_layout.addWidget(browse_source_btn, 0, 2)

        # 整理先
        dir_layout.addWidget(QLabel("整理先:"), 1, 0)
        self.output_dir_edit = QLineEdit()
        dir_layout.addWidget(self.output_dir_edit, 1, 1)
        browse_output_btn = QPushButton("参照")
        browse_output_btn.clicked.connect(self._browse_output_dir)
        dir_layout.addWidget(browse_output_btn, 1, 2)

        # 同じディレクトリチェックボックス
        self.same_dir_check = QCheckBox("同じディレクトリ内で整理（整理先は無視）")
        dir_layout.addWidget(self.same_dir_check, 2, 1)

        dir_group.setLayout(dir_layout)
        main_layout.addWidget(dir_group)

        # 中央: ルールとオプション
        middle_layout = QHBoxLayout()

        # 左: ルール情報
        rule_group = QGroupBox("現在のルール")
        rule_layout = QVBoxLayout()

        self.rule_text = QTextEdit()
        self.rule_text.setReadOnly(True)
        self.rule_text.setMaximumHeight(200)
        rule_layout.addWidget(self.rule_text)

        rule_btn_layout = QHBoxLayout()
        edit_rule_btn = QPushButton("ルール編集")
        edit_rule_btn.clicked.connect(self._edit_rule)
        rule_btn_layout.addWidget(edit_rule_btn)

        reset_rule_btn = QPushButton("デフォルトに戻す")
        reset_rule_btn.clicked.connect(self._load_default_rule)
        rule_btn_layout.addWidget(reset_rule_btn)

        rule_layout.addLayout(rule_btn_layout)
        rule_group.setLayout(rule_layout)
        middle_layout.addWidget(rule_group, stretch=2)

        # 右: オプション
        options_group = QGroupBox("オプション")
        options_layout = QVBoxLayout()

        # バックアップオプション
        self.backup_check = QCheckBox("整理前にバックアップを作成")
        self.backup_check.setChecked(True)
        options_layout.addWidget(self.backup_check)

        # 操作モード
        options_layout.addWidget(QLabel("操作モード:"))
        self.operation_mode_group = QButtonGroup()
        self.move_radio = QRadioButton("移動")
        self.move_radio.setChecked(True)
        self.copy_radio = QRadioButton("コピー")
        self.operation_mode_group.addButton(self.move_radio, 0)
        self.operation_mode_group.addButton(self.copy_radio, 1)

        mode_layout = QVBoxLayout()
        mode_layout.setContentsMargins(20, 0, 0, 0)
        mode_layout.addWidget(self.move_radio)
        mode_layout.addWidget(self.copy_radio)
        options_layout.addLayout(mode_layout)

        # 既存ファイル処理
        options_layout.addWidget(QLabel("既存ファイル:"))
        self.skip_existing_check = QCheckBox("スキップする")
        self.skip_existing_check.setChecked(True)
        skip_layout = QVBoxLayout()
        skip_layout.setContentsMargins(20, 0, 0, 0)
        skip_layout.addWidget(self.skip_existing_check)
        options_layout.addLayout(skip_layout)

        # フォルダ監視
        options_layout.addSpacing(10)
        options_layout.addWidget(QLabel("自動整理:"))
        self.watch_button = QPushButton("監視開始")
        self.watch_button.clicked.connect(self._toggle_watch)
        options_layout.addWidget(self.watch_button)

        self.watch_status_label = QLabel("停止中")
        self.watch_status_label.setStyleSheet("color: gray;")
        self.watch_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        options_layout.addWidget(self.watch_status_label)

        options_layout.addStretch()

        options_group.setLayout(options_layout)
        middle_layout.addWidget(options_group, stretch=1)

        main_layout.addLayout(middle_layout)

        # アクションボタン
        action_layout = QHBoxLayout()

        preview_btn = QPushButton("プレビュー")
        preview_btn.clicked.connect(self._preview_organization)
        preview_btn.setMinimumHeight(35)
        action_layout.addWidget(preview_btn)

        execute_btn = QPushButton("整理実行")
        execute_btn.setObjectName("accentButton")
        execute_btn.clicked.connect(self._execute_organization)
        execute_btn.setMinimumHeight(35)
        action_layout.addWidget(execute_btn)

        undo_btn = QPushButton("元に戻す")
        undo_btn.clicked.connect(self._undo_last_operation)
        undo_btn.setMinimumHeight(35)
        action_layout.addWidget(undo_btn)

        main_layout.addLayout(action_layout)

        central_widget.setLayout(main_layout)

        # ステータスバー
        self.statusBar().showMessage("準備完了")

    def _browse_source_dir(self) -> None:
        """整理元ディレクトリを選択"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "整理元ディレクトリを選択"
        )
        if directory:
            self.source_dir_edit.setText(directory)

    def _browse_output_dir(self) -> None:
        """整理先ディレクトリを選択"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "整理先ディレクトリを選択"
        )
        if directory:
            self.output_dir_edit.setText(directory)

    def _open_rule(self) -> None:
        """ルールファイルを開く"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "ルールファイルを開く",
            "data/rules",
            "JSONファイル (*.json);;すべてのファイル (*.*)"
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
            QMessageBox.warning(self, "警告", "保存するルールがありません")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "ルールを保存",
            "data/rules",
            "JSONファイル (*.json);;すべてのファイル (*.*)"
        )

        if file_path:
            if self.rule_engine.save_rules(self.current_rules, file_path):
                self.update_status(f"ルールを保存しました: {file_path}")

    def _edit_rule(self) -> None:
        """ルールを編集"""
        dialog = RuleEditorDialog(self, self.current_rules)

        if dialog.exec_centered():
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

        text = f"ルール名: {self.current_rules.get('name', '不明')}\n\n"
        text += f"説明: {self.current_rules.get('description', 'なし')}\n\n"
        text += "有効なルール:\n"

        for rule in self.current_rules.get('rules', []):
            if rule.get('enabled', True):
                rule_type = rule.get('type', '不明')
                text += f"  - {rule_type}\n"

        self.rule_text.setPlainText(text)

    def _preview_organization(self) -> None:
        """整理のプレビューを表示"""
        source_dir = self.source_dir_edit.text()

        if not source_dir:
            QMessageBox.critical(self, "エラー", "有効な整理元ディレクトリを選択してください")
            return

        if not self.current_rules:
            QMessageBox.critical(self, "エラー", "ルールが設定されていません")
            return

        # 進捗ダイアログを表示（キャンセル可能）
        self.current_progress_dialog = IndeterminateProgressDialog(
            self,
            title="プレビュー生成中",
            message="整理内容を分析しています...",
            cancelable=True
        )

        # ワーカーで実行
        output_dir = self.output_dir_edit.text() or source_dir
        operation_mode = "move" if self.move_radio.isChecked() else "copy"

        self.current_worker = OrganizeWorker(
            self.organizer,
            source_dir,
            self.current_rules,
            output_dir,
            preview_mode=True,
            operation_mode=operation_mode
        )

        self.current_worker.finished.connect(
            lambda actions: self._show_preview_dialog(actions)
        )
        self.current_worker.error.connect(
            lambda error: self._handle_worker_error_with_cleanup(error)
        )

        # キャンセルボタンとワーカーを接続
        def check_cancel():
            if self.current_progress_dialog and self.current_progress_dialog.is_cancelled:
                # タイマーを即座に停止
                if self.cancel_timer:
                    self.cancel_timer.stop()
                    self.cancel_timer.deleteLater()
                    self.cancel_timer = None

                # ワーカーをキャンセル
                if self.current_worker:
                    self.current_worker.cancel()
                    self.current_worker.quit()
                    self.current_worker.wait()
                    self.current_worker = None

                # ダイアログを閉じる
                if self.current_progress_dialog:
                    self.current_progress_dialog.close()
                    self.current_progress_dialog.deleteLater()
                    self.current_progress_dialog = None

                self.update_status("プレビュー生成をキャンセルしました")

        # 定期的にキャンセルチェック
        self.cancel_timer = QTimer(self)
        self.cancel_timer.timeout.connect(check_cancel)
        self.cancel_timer.start(100)  # 100msごとにチェック

        # ワーカー終了時にクリーンアップ
        self.current_worker.finished.connect(self._cleanup_preview_resources)
        self.current_worker.error.connect(self._cleanup_preview_resources)

        self.current_progress_dialog.show()
        self.current_worker.start()

    def _cleanup_preview_resources(self) -> None:
        """プレビュー処理のリソースをクリーンアップ"""
        # タイマー停止
        if self.cancel_timer:
            self.cancel_timer.stop()
            self.cancel_timer.deleteLater()
            self.cancel_timer = None

        # 進捗ダイアログを閉じる
        if self.current_progress_dialog:
            self.current_progress_dialog.close()
            self.current_progress_dialog.deleteLater()
            self.current_progress_dialog = None

    def _show_preview_dialog(self, actions) -> None:
        """プレビューダイアログを表示"""
        # クリーンアップは finished シグナルで既に実行されている

        if not actions:
            QMessageBox.information(self, "情報", "整理するファイルがありません")
            return

        # プレビューダイアログを表示
        preview_dialog = PreviewDialog(self, actions)

        if preview_dialog.exec_centered():
            confirmed_actions = preview_dialog.get_confirmed_actions()
            if confirmed_actions:
                self.current_actions = confirmed_actions
                # 実行確認
                reply = QMessageBox.question(
                    self,
                    "確認",
                    f"{len(confirmed_actions)}件のファイルを整理しますか？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self._execute_with_actions(confirmed_actions)

    def _execute_organization(self) -> None:
        """整理を実行"""
        source_dir = self.source_dir_edit.text()

        if not source_dir:
            QMessageBox.critical(self, "エラー", "有効な整理元ディレクトリを選択してください")
            return

        if not self.current_rules:
            QMessageBox.critical(self, "エラー", "ルールが設定されていません")
            return

        # 確認
        reply = QMessageBox.question(
            self,
            "確認",
            "ファイルの整理を実行しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # バックアップ作成
        if self.backup_check.isChecked():
            self.current_progress_dialog = IndeterminateProgressDialog(
                self,
                title="バックアップ作成中",
                message="整理前のバックアップを作成しています..."
            )
            self.current_progress_dialog.show()

            self.current_worker = BackupWorker(self.backup_manager, source_dir)
            self.current_worker.finished.connect(
                lambda backup_id: self._after_backup(backup_id, self.current_progress_dialog)
            )
            self.current_worker.error.connect(
                lambda error: self._handle_worker_error(error, self.current_progress_dialog)
            )
            self.current_worker.start()
        else:
            self._execute_organization_worker()

    def _after_backup(self, backup_id: str, progress_dialog) -> None:
        """バックアップ後の処理"""
        progress_dialog.close()
        if backup_id:
            self.update_status(f"バックアップを作成しました: {backup_id}")
        self._execute_organization_worker()

    def _execute_organization_worker(self) -> None:
        """整理を実行（ワーカー）"""
        source_dir = self.source_dir_edit.text()
        output_dir = self.output_dir_edit.text() or source_dir

        # アクション生成（まだ生成していない場合）
        if not self.current_actions:
            operation_mode = "move" if self.move_radio.isChecked() else "copy"
            self.current_actions = self.organizer.organize(
                source_dir,
                self.current_rules,
                output_dir,
                preview_mode=False,
                operation_mode=operation_mode
            )

        if not self.current_actions:
            QMessageBox.information(self, "情報", "整理するファイルがありません")
            return

        self._execute_with_actions(self.current_actions)

    def _execute_with_actions(self, actions) -> None:
        """アクションを実行"""
        # 進捗ダイアログを表示
        self.current_progress_dialog = ProgressDialog(
            self,
            title="整理実行中",
            total_items=len(actions)
        )
        self.current_progress_dialog.show()

        # ワーカーで実行
        self.current_worker = ExecuteWorker(
            self.organizer,
            actions,
            skip_existing=self.skip_existing_check.isChecked()
        )

        self.current_worker.progress.connect(
            lambda current, total, message: self.current_progress_dialog.update_progress(current, message)
        )
        self.current_worker.finished.connect(
            lambda result: self._after_execute(result, self.current_progress_dialog)
        )
        self.current_worker.error.connect(
            lambda error: self._handle_worker_error(error, self.current_progress_dialog)
        )

        self.current_worker.start()

    def _after_execute(self, result, progress_dialog) -> None:
        """実行後の処理"""
        progress_dialog.complete("完了しました")

        # 完了メッセージ
        success_msg = f"整理が完了しました\n\n"
        success_msg += f"成功: {result['successful']}件\n"
        success_msg += f"失敗: {result['failed']}件\n"
        success_msg += f"スキップ: {result['skipped']}件"

        QMessageBox.information(self, "完了", success_msg)
        self.update_status("整理が完了しました")

        # アクションをクリア
        self.current_actions = []

    def _undo_last_operation(self) -> None:
        """最後の操作を元に戻す"""
        # 最新のログファイルを取得
        logs = self.organizer.logger.list_logs(limit=1)

        if not logs:
            QMessageBox.information(self, "情報", "元に戻す操作がありません")
            return

        log_file = logs[0]["path"]

        # 確認
        reply = QMessageBox.question(
            self,
            "確認",
            f"最後の操作を元に戻しますか？\n\n操作: {logs[0]['operation_name']}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 進捗ダイアログを表示
        self.current_progress_dialog = IndeterminateProgressDialog(
            self,
            title="元に戻し中",
            message="操作を元に戻しています..."
        )
        self.current_progress_dialog.show()

        # ワーカーで実行
        self.current_worker = UndoWorker(self.organizer, log_file)
        self.current_worker.finished.connect(
            lambda success: self._after_undo(success, self.current_progress_dialog)
        )
        self.current_worker.error.connect(
            lambda error: self._handle_worker_error(error, self.current_progress_dialog)
        )
        self.current_worker.start()

    def _after_undo(self, success: bool, progress_dialog) -> None:
        """元に戻し後の処理"""
        progress_dialog.close()

        if success:
            QMessageBox.information(self, "完了", "操作を元に戻しました")
            self.update_status("操作を元に戻しました")
        else:
            QMessageBox.critical(self, "エラー", "操作を元に戻せませんでした")

    def _toggle_watch(self) -> None:
        """フォルダ監視の開始/停止を切り替え"""
        if self.watcher and self.watcher.is_active():
            # 監視停止
            self.watcher.stop_watching()
            self.watcher = None
            self.watch_button.setText("監視開始")
            self.watch_status_label.setText("停止中")
            self.watch_status_label.setStyleSheet("color: gray;")
            self.update_status("フォルダ監視を停止しました")
        else:
            # 監視開始
            source_dir = self.source_dir_edit.text()

            if not source_dir:
                QMessageBox.critical(self, "エラー", "有効なディレクトリを選択してください")
                return

            if not self.current_rules:
                QMessageBox.critical(self, "エラー", "ルールが設定されていません")
                return

            def watch_callback(event_type, file_path):
                import os
                self.update_status(f"自動整理: {os.path.basename(file_path)}")

            self.watcher = FolderWatcher(self.organizer)
            if self.watcher.start_watching(source_dir, self.current_rules, watch_callback):
                self.watch_button.setText("監視停止")
                self.watch_status_label.setText("監視中")
                self.watch_status_label.setStyleSheet("color: green;")
                self.update_status(f"フォルダ監視を開始しました: {source_dir}")

    def _change_theme(self, theme: ThemeType) -> None:
        """テーマを変更"""
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        ThemeManager.apply_theme(app, theme)
        self.update_status(f"テーマを変更しました: {theme.value}")

    def _detect_duplicates(self) -> None:
        """重複ファイルを検出"""
        QMessageBox.information(self, "情報", "重複ファイル検出機能は実装中です")

    def _manage_backups(self) -> None:
        """バックアップ管理"""
        QMessageBox.information(self, "情報", "バックアップ管理機能は実装中です")

    def _view_logs(self) -> None:
        """ログビューア"""
        QMessageBox.information(self, "情報", "ログビューア機能は実装中です")

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
- テーマ切り替え（設定メニュー）
        """
        QMessageBox.information(self, "使い方", help_text.strip())

    def _show_about(self) -> None:
        """バージョン情報を表示"""
        about_text = """
File Organizer
Version 2.0.0 (PyQt6)

フル機能のファイル整理ツール

(c) 2026
        """
        QMessageBox.information(self, "バージョン情報", about_text.strip())

    def _handle_worker_error(self, error: str, progress_dialog=None) -> None:
        """ワーカーエラーの処理"""
        if progress_dialog:
            progress_dialog.close()
        QMessageBox.critical(self, "エラー", f"エラーが発生しました:\n{error}")

    def _handle_worker_error_with_cleanup(self, error: str) -> None:
        """ワーカーエラーの処理（クリーンアップは既にシグナルで実行済み）"""
        QMessageBox.critical(self, "エラー", f"エラーが発生しました:\n{error}")

    def update_status(self, message: str) -> None:
        """ステータスバーを更新"""
        self.statusBar().showMessage(message)
