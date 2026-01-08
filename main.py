import sys
import os
from PySide6.QtWidgets import QApplication

# ROOT_PATH: balise_tester
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from balise_tester.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
