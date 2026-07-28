from pathlib import Path
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import QFileDialog, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QMessageBox, QPushButton, QTextEdit, QVBoxLayout, QWizardPage
from wkcalc.explanations import result_summary
from wkcalc.exports import record_to_json, result_to_csv, result_to_html
from wkcalc.models import CalculationRecord
from wkcalc.persistence import application_data_dir, safe_filename

class ResultsPage(QWizardPage):
    def __init__(self):
        super().__init__(); self.setTitle("Result and export"); self.setSubTitle("All files are written locally."); layout=QVBoxLayout(self); self.box=QGroupBox("Calculation result"); self.form=QFormLayout(self.box); self.rule=QLabel(); self.rule.setWordWrap(True); self.explanation=QTextEdit(); self.explanation.setReadOnly(True); buttons=QHBoxLayout()
        for label,handler in (("Save calculation",self.save_json),("Export CSV",self.save_csv),("Export HTML",self.save_html),("Print",self.print_report)):
            button=QPushButton(label); button.clicked.connect(handler); buttons.addWidget(button)
        layout.addWidget(self.box); layout.addWidget(QLabel("Exact rule path")); layout.addWidget(self.rule); layout.addWidget(self.explanation); layout.addLayout(buttons)
    def initializePage(self):
        while self.form.rowCount(): self.form.removeRow(0)
        for label,value in result_summary(self.wizard().result): self.form.addRow(label,QLabel(f"<b>{value}</b>" if label=="Final Wk" else value))
        self.rule.setText(self.wizard().result.rule_path); self.explanation.setPlainText("\n\n".join(self.wizard().result.explanation))
    def _record(self): return CalculationRecord(project=self.wizard().project,road=self.wizard().road)
    def _path(self,title,suffix,subfolder="exports"):
        folder=application_data_dir()/subfolder; suggested=folder/f"{safe_filename(self.wizard().project.calculation_reference)}.{suffix}"; name,_=QFileDialog.getSaveFileName(self,title,str(suggested),f"{suffix.upper()} (*.{suffix})"); return Path(name) if name else None
    def _write(self,title,suffix,content,subfolder="exports"):
        path=self._path(title,suffix,subfolder)
        if path: path.write_text(content,encoding="utf-8",newline=""); QMessageBox.information(self,"Export complete",f"Saved locally to:\n{path}")
    def save_json(self): self._write("Save calculation","json",record_to_json(self._record(),self.wizard().result),"calculations")
    def save_csv(self): self._write("Export result","csv",result_to_csv(self._record(),self.wizard().result))
    def save_html(self): self._write("Export report","html",result_to_html(self._record(),self.wizard().result))
    def print_report(self):
        printer=QPrinter(QPrinter.PrinterMode.HighResolution); dialog=QPrintDialog(printer,self)
        if dialog.exec(): document=QTextDocument(); document.setHtml(result_to_html(self._record(),self.wizard().result)); document.print_(printer)
