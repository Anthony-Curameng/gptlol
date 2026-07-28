"""Native offline desktop entry point."""
import sys
from PySide6.QtWidgets import QApplication,QMessageBox
from wkcalc.constants import APPLICATION_NAME,ORGANISATION_NAME
from wkcalc.persistence import recover_autosave
from wkcalc.ui import create_main_window
def main():
    app=QApplication(sys.argv); app.setApplicationName(APPLICATION_NAME); app.setOrganizationName(ORGANISATION_NAME); window=create_main_window(); autosave=recover_autosave()
    if autosave is not None and QMessageBox.question(window,"Recover autosave?","A valid autosave from an abnormal shutdown was found. Recover it now?")==QMessageBox.StandardButton.Yes: window.restore_record(autosave)
    window.show(); return app.exec()
if __name__=="__main__":raise SystemExit(main())
