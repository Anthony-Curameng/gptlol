from PySide6.QtWidgets import QLabel, QVBoxLayout, QWizardPage
from wkcalc.calculator import calculate_wk
from .cross_section import CrossSectionView

class ReviewPage(QWizardPage):
    def __init__(self):
        super().__init__(); self.setTitle("Review geometry"); self.setSubTitle("Confirm the local cross-section before calculating."); layout=QVBoxLayout(self); self.summary=QLabel(); self.view=CrossSectionView(); layout.addWidget(self.summary); layout.addWidget(self.view)
    def initializePage(self):
        result=calculate_wk(self.wizard().road,self.wizard().elements); self.wizard().result=result; self.summary.setText(f"Travelled way: {result.travelled_width_m:.2f} m   •   Unrestricted Wk: {result.unrestricted_wk_m:.2f} m   •   Proposed final Wk: {result.final_wk_m:.2f} m"); self.view.draw_geometry(self.wizard().road,result,self.wizard().elements)
