from PySide6.QtCore import QSize
from pathlib import Path
from PySide6.QtWidgets import QFileDialog,QMessageBox,QWizard
from ..enums import AuthorityRule,WidthInputMode
from ..models import RoadInput
from ..persistence import clear_autosave,load_record
from .pages import ArrangementPage,AuthorityPage,CrossSectionPage,LeftBoundaryPage,ReviewPage,RightBoundaryPage,ResultPage
class CalculatorWizard(QWizard):
    ARRANGEMENT,CROSS_SECTION,LEFT,RIGHT,AUTHORITY,REVIEW,RESULT=range(7)
    def __init__(self):
        super().__init__(); self.setWindowTitle("Wk Calculator"); self.setMinimumSize(QSize(1000,720)); self.setWizardStyle(QWizard.WizardStyle.ModernStyle); self.dirty=True; self.road_input=None; self.result=None
        self.arrangement_page=ArrangementPage(); self.cross_section_page=CrossSectionPage(); self.left_boundary_page=LeftBoundaryPage(); self.right_boundary_page=RightBoundaryPage(); self.authority_page=AuthorityPage(); self.review_page=ReviewPage(); self.result_page=ResultPage()
        for page_id,page in enumerate((self.arrangement_page,self.cross_section_page,self.left_boundary_page,self.right_boundary_page,self.authority_page,self.review_page,self.result_page)):self.setPage(page_id,page)
        self.setStartId(self.ARRANGEMENT); self.currentIdChanged.connect(lambda _:setattr(self,"dirty",True)); self.setOption(QWizard.WizardOption.HaveCustomButton1,True); self.setButtonText(QWizard.WizardButton.CustomButton1,"Open Calculation…"); self.customButtonClicked.connect(self._open)
    def nextId(self):
        current=self.currentId()
        if current==self.CROSS_SECTION and self.cross_section_page.full.isChecked():return self.AUTHORITY
        return super().nextId()
    def build_road(self):
        cross=self.cross_section_page; authority=self.authority_page; full=cross.full.isChecked(); mode=cross.width_mode()
        return RoadInput(arrangement=self.arrangement_page.arrangement.currentData(),width_mode=mode,simple_internal_width_m=cross.width.value() if mode==WidthInputMode.SIMPLE and not full else None,segments=cross.editor.segments() if mode==WidthInputMode.DETAILED and not full else (),full_kerb_to_kerb_is_travelled=full,kerb_to_kerb_width_m=cross.width.value() if full else (cross.total.value() if cross.verify_total.isChecked() else None),left_boundary=None if full else self.left_boundary_page.boundary(),right_boundary=None if full else self.right_boundary_page.boundary(),authority_rule=authority.rule.currentData(),authority_width_m=authority.width.value() if authority.rule.currentData()!=AuthorityRule.NONE else None,authority_name=authority.name.text().strip() if authority.rule.currentData()!=AuthorityRule.NONE else "",authority_reference=authority.reference.text().strip() if authority.rule.currentData()!=AuthorityRule.NONE else "",project_name=self.arrangement_page.project.text().strip(),road_name=self.arrangement_page.road.text().strip(),section_reference=self.arrangement_page.section.text().strip(),calculation_notes=self.arrangement_page.notes.text().strip(),physical_median_present=self.arrangement_page.median.isChecked())
    def restart_calculation(self):
        self.setStartId(self.ARRANGEMENT); self.arrangement_page.arrangement.setCurrentIndex(0); self.arrangement_page.median.setChecked(False)
        for field in (self.arrangement_page.project,self.arrangement_page.road,self.arrangement_page.section,self.arrangement_page.notes):field.clear()
        self.cross_section_page.full.setChecked(False); self.cross_section_page.simple.setChecked(True); self.cross_section_page.width.setValue(0); self.cross_section_page.verify_total.setChecked(False); self.cross_section_page.total.setValue(0); self.cross_section_page.editor.table.setRowCount(0)
        for page in (self.left_boundary_page,self.right_boundary_page):page.edge.setCurrentIndex(0);page.distance.setValue(0);page.allowance.setValue(0)
        self.authority_page.rule.setCurrentIndex(0);self.authority_page.name.clear();self.authority_page.reference.clear();self.authority_page.width.setValue(0);self.road_input=None;self.result=None;self.dirty=False;self.restart()
    def _open(self,button):
        if button!=QWizard.WizardButton.CustomButton1:return
        filename,_=QFileDialog.getOpenFileName(self,"Open calculation","","Wk Calculator (*.wkcalc.json);;JSON (*.json)")
        if not filename:return
        try:self.restore_record(load_record(Path(filename)))
        except (OSError,ValueError) as error:QMessageBox.warning(self,"Could not open calculation",str(error))
    def restore_record(self,record):
        road=record.road_input; arrangement=self.arrangement_page; arrangement.arrangement.setCurrentIndex(arrangement.arrangement.findData(road.arrangement)); arrangement.median.setChecked(road.physical_median_present); arrangement.project.setText(road.project_name); arrangement.road.setText(road.road_name); arrangement.section.setText(road.section_reference); arrangement.notes.setText(road.calculation_notes)
        cross=self.cross_section_page; cross.full.setChecked(road.full_kerb_to_kerb_is_travelled); cross.simple.setChecked(road.width_mode==WidthInputMode.SIMPLE); cross.detailed.setChecked(road.width_mode==WidthInputMode.DETAILED); cross.width.setValue(road.kerb_to_kerb_width_m if road.full_kerb_to_kerb_is_travelled else (road.simple_internal_width_m or 0)); cross.editor.table.setRowCount(0)
        for segment in road.segments:cross.editor.add_segment(segment.segment_type,segment.label,segment.width_m,segment.quantity)
        cross.verify_total.setChecked(not road.full_kerb_to_kerb_is_travelled and road.kerb_to_kerb_width_m is not None); cross.total.setValue(road.kerb_to_kerb_width_m or 0)
        if road.left_boundary:self.left_boundary_page.load_boundary(road.left_boundary)
        if road.right_boundary:self.right_boundary_page.load_boundary(road.right_boundary)
        authority=self.authority_page; authority.rule.setCurrentIndex(authority.rule.findData(road.authority_rule)); authority.name.setText(road.authority_name); authority.reference.setText(road.authority_reference); authority.width.setValue(road.authority_width_m or 0)
        self.road_input=road; self.result=record.result; self.dirty=False; self.setStartId(self.REVIEW); self.restart()
    def closeEvent(self,event):
        if self.dirty and QMessageBox.question(self,"Close Wk Calculator?","Unsaved changes will be discarded. Close anyway?")!=QMessageBox.StandardButton.Yes:event.ignore();return
        clear_autosave();event.accept()
