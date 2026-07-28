"""Application window factory and installed desktop entry point."""
import sys
from PySide6.QtWidgets import QApplication
from .wizard import WkWizard

def create_main_window() -> WkWizard:
    return WkWizard()

def main() -> int:
    application = QApplication(sys.argv)
    application.setApplicationName("Wk Calculator")
    application.setOrganizationName("Wk Calculator")
    window = create_main_window()
    window.show()
    return application.exec()
