from PySide6.QtWidgets import QWidget
from ui.about import Ui_aboutForm

class AboutWindow(QWidget, Ui_aboutForm):
    """关于窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
