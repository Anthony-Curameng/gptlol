from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QFileDialog,QHBoxLayout,QLabel,QMessageBox,QPushButton,QTextEdit,QVBoxLayout,QWizardPage
from ...exports import export_csv,export_json,export_pdf
from ...models import CalculationRecord
from ...persistence import clear_autosave,default_exports_dir,last_used_folder,remember_last_folder,save_record
from ..widgets import HelpPanel,ResultSummary
class ResultPage(QWizardPage):
    def __init__(self):
        super().__init__(); self.setTitle("Result and export"); layout=QVBoxLayout(self); self.summary=ResultSummary(); self.arithmetic=QLabel(); self.arithmetic.setStyleSheet("font-family:Consolas;font-size:12pt"); self.trace=QTextEdit(); self.trace.setReadOnly(True); self.warnings=QLabel(); self.warnings.setStyleSheet("color:#a04b00"); self.warnings.setWordWrap(True); buttons=QHBoxLayout()
        for text,handler in (("Save Calculation",self.save),("Export PDF",self.pdf),("Export JSON",self.json),("Export CSV",self.csv),("Copy Summary",self.copy),("Start New Calculation",self.reset)):
            button=QPushButton(text); button.clicked.connect(handler); buttons.addWidget(button)
        layout.addWidget(self.summary); layout.addWidget(self.arithmetic); layout.addWidget(self.warnings); layout.addWidget(QLabel("Rule trace")); layout.addWidget(self.trace); layout.addLayout(buttons); layout.addWidget(HelpPanel("Physical Wk comes from the entered geometry. Any authority adjustment is shown separately and never silently changes the physical result.")); self.record=None
    def initializePage(self):
        result=self.wizard().result; self.summary.set_result(result); self.arithmetic.setText(f"Internal span       {result.internal_width_m:8.2f} m\nLeft allowance      {result.left_allowance_m:8.2f} m\nRight allowance     {result.right_allowance_m:8.2f} m\n                    -----------\nPhysical Wk         {result.physical_wk_m:8.2f} m\nFinal Wk            {result.final_wk_m:8.2f} m"); self.trace.setPlainText("\n\n".join(result.rule_trace)); self.warnings.setText("\n".join(f"⚠ {w}" for w in result.warnings)); self.record=CalculationRecord(road_input=self.wizard().road_input,result=result)
    def _folder(self):return str(last_used_folder(default_exports_dir()))
    def _path(self,title,filter,suffix):
        name,_=QFileDialog.getSaveFileName(self,title,self._folder(),filter)
        if not name:return None
        path=Path(name); path=path if str(path).lower().endswith(suffix) else Path(str(path)+suffix); remember_last_folder(path.parent); return path
    def save(self):
        path=self._path("Save calculation","Wk Calculator (*.wkcalc.json)",".wkcalc.json")
        if path:self.record=save_record(self.record,path); self.wizard().dirty=False; clear_autosave(); QMessageBox.information(self,"Saved",str(path))
    def pdf(self):
        path=self._path("Export PDF","PDF (*.pdf)",".pdf")
        if path:export_pdf(self.record,path,self.wizard().review_page.diagram)
    def json(self):
        path=self._path("Export JSON","JSON (*.json)",".json")
        if path:path.write_text(export_json(self.record),encoding="utf-8")
    def csv(self):
        path=self._path("Export CSV","CSV (*.csv)",".csv")
        if path:path.write_text(export_csv(self.record),encoding="utf-8-sig",newline="")
    def copy(self):QGuiApplication.clipboard().setText(self.arithmetic.text()+"\n\n"+self.trace.toPlainText())
    def reset(self):
        if self.wizard().dirty and QMessageBox.question(self,"Start new calculation?","Unsaved changes will be discarded. Continue?")!=QMessageBox.StandardButton.Yes:return
        clear_autosave(); self.wizard().restart_calculation()
