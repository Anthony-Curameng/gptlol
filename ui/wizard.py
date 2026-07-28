from pathlib import Path
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QFileDialog, QMessageBox, QWizard
from wkcalc.models import ProjectDetails
from wkcalc.persistence import load_record
from .limits_page import LimitsPage
from .project_page import ProjectPage
from .results_page import ResultsPage
from .review_page import ReviewPage
from .side_page import SidePage
from .travelled_way_page import TravelledWayPage

class WkWizard(QWizard):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Wk Calculator"); self.setWizardStyle(QWizard.WizardStyle.ModernStyle); self.setOption(QWizard.WizardOption.HaveHelpButton,False); self.setMinimumSize(QSize(900,650)); self.project=ProjectDetails(); self.elements=[]; self.travelled_width_m=10.5; self.left=self.right=self.road=self.result=None
        self.project_page=ProjectPage(); self.travelled_page=TravelledWayPage(); self.left_page=SidePage("left"); self.right_page=SidePage("right"); self.limits_page=LimitsPage()
        for page in (self.project_page,self.travelled_page,self.left_page,self.right_page,self.limits_page,ReviewPage(),ResultsPage()): self.addPage(page)
        self.setButtonText(QWizard.WizardButton.FinishButton,"Close")
        self.setOption(QWizard.WizardOption.HaveCustomButton1,True); self.setButtonText(QWizard.WizardButton.CustomButton1,"Load calculation…"); self.customButtonClicked.connect(self._load)

    def _load(self, button):
        if button != QWizard.WizardButton.CustomButton1: return
        filename,_=QFileDialog.getOpenFileName(self,"Load calculation","","Wk calculations (*.json)")
        if not filename: return
        try: record=load_record(Path(filename))
        except (OSError,ValueError) as error: QMessageBox.warning(self,"Could not load calculation",str(error)); return
        self.project, self.road = record.project, record.road; self.travelled_width_m=record.road.travelled_width_m; self.left=record.road.left; self.right=record.road.right; self.elements=[]
        self.project_page.load_details(record.project); self.travelled_page.load_width(record.road.travelled_width_m); self.left_page.load_side(record.road.left); self.right_page.load_side(record.road.right); self.limits_page.load_road(record.road); self.restart()
