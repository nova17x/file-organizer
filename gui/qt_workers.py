"""
QThreadワーカークラス (PyQt6版)
長時間実行される操作のためのワーカースレッド
"""

from PyQt6.QtCore import QThread, pyqtSignal
from typing import Dict, List, Optional, Any, Callable


class OrganizeWorker(QThread):
    """整理操作のワーカースレッド"""

    # シグナル
    finished = pyqtSignal(list)  # actions
    error = pyqtSignal(str)  # error message

    def __init__(
        self,
        organizer,
        source_dir: str,
        rules: Dict,
        output_dir: str,
        preview_mode: bool,
        operation_mode: str
    ):
        super().__init__()
        self.organizer = organizer
        self.source_dir = source_dir
        self.rules = rules
        self.output_dir = output_dir
        self.preview_mode = preview_mode
        self.operation_mode = operation_mode
        self._is_cancelled = False

    def cancel(self):
        """処理をキャンセル"""
        self._is_cancelled = True

    def run(self):
        """スレッド実行"""
        try:
            actions = self.organizer.organize(
                self.source_dir,
                self.rules,
                self.output_dir,
                preview_mode=self.preview_mode,
                operation_mode=self.operation_mode
            )
            if not self._is_cancelled:
                self.finished.emit(actions)
        except Exception as e:
            if not self._is_cancelled:
                self.error.emit(str(e))


class ExecuteWorker(QThread):
    """実行操作のワーカースレッド"""

    # シグナル
    progress = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(dict)  # result
    error = pyqtSignal(str)  # error message

    def __init__(
        self,
        organizer,
        actions: List[Dict],
        skip_existing: bool
    ):
        super().__init__()
        self.organizer = organizer
        self.actions = actions
        self.skip_existing = skip_existing

    def run(self):
        """スレッド実行"""
        try:
            def progress_callback(current: int, total: int, message: str):
                self.progress.emit(current, total, message)

            result = self.organizer.execute_actions(
                self.actions,
                callback=progress_callback,
                skip_existing=self.skip_existing
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class UndoWorker(QThread):
    """元に戻す操作のワーカースレッド"""

    # シグナル
    finished = pyqtSignal(bool)  # success
    error = pyqtSignal(str)  # error message

    def __init__(self, organizer, log_file: str):
        super().__init__()
        self.organizer = organizer
        self.log_file = log_file

    def run(self):
        """スレッド実行"""
        try:
            success = self.organizer.undo(self.log_file)
            self.finished.emit(success)
        except Exception as e:
            self.error.emit(str(e))


class BackupWorker(QThread):
    """バックアップ作成のワーカースレッド"""

    # シグナル
    finished = pyqtSignal(str)  # backup_id
    error = pyqtSignal(str)  # error message

    def __init__(self, backup_manager, source_dir: str):
        super().__init__()
        self.backup_manager = backup_manager
        self.source_dir = source_dir

    def run(self):
        """スレッド実行"""
        try:
            backup_id = self.backup_manager.create_backup(self.source_dir)
            self.finished.emit(backup_id or "")
        except Exception as e:
            self.error.emit(str(e))
