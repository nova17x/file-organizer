"""
ベースウィンドウクラス
すべてのウィンドウとダイアログの共通機能を提供
"""

from PyQt6.QtWidgets import QMainWindow, QDialog
from PyQt6.QtCore import Qt
from typing import Optional


class BaseWindow(QMainWindow):
    """メインウィンドウの基底クラス"""

    def __init__(self, parent: Optional[QMainWindow] = None):
        super().__init__(parent)
        self._setup_window()

    def _setup_window(self) -> None:
        """ウィンドウの基本設定"""
        # ウィンドウフラグの設定
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint
        )

    def center_on_screen(self) -> None:
        """ウィンドウを画面中央に配置"""
        screen_geometry = self.screen().geometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def center_on_parent(self) -> None:
        """親ウィンドウの中央に配置"""
        if self.parent():
            parent_geometry = self.parent().frameGeometry()
            window_geometry = self.frameGeometry()
            center_point = parent_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())


class BaseDialog(QDialog):
    """ダイアログの基底クラス"""

    def __init__(self, parent: Optional[QMainWindow] = None, modal: bool = True):
        super().__init__(parent)
        self._setup_dialog(modal)

    def _setup_dialog(self, modal: bool) -> None:
        """ダイアログの基本設定"""
        # モーダル設定
        self.setModal(modal)

        # ウィンドウフラグの設定
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowCloseButtonHint
        )

    def center_on_screen(self) -> None:
        """ダイアログを画面中央に配置"""
        screen_geometry = self.screen().geometry()
        dialog_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        dialog_geometry.moveCenter(center_point)
        self.move(dialog_geometry.topLeft())

    def center_on_parent(self) -> None:
        """親ウィンドウの中央に配置"""
        if self.parent():
            parent_geometry = self.parent().frameGeometry()
            dialog_geometry = self.frameGeometry()
            center_point = parent_geometry.center()
            dialog_geometry.moveCenter(center_point)
            self.move(dialog_geometry.topLeft())
        else:
            self.center_on_screen()

    def show_centered(self) -> None:
        """中央に配置して表示"""
        self.center_on_parent()
        self.show()

    def exec_centered(self) -> int:
        """中央に配置してモーダル表示"""
        self.center_on_parent()
        return self.exec()
