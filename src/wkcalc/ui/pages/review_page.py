from PySide6.QtWidgets import QLabel,QVBoxLayout,QWizardPage
from ...calculator import calculate_wk
from ...enums import EdgeReferenceType,SegmentType,SurfaceType
from ...validation import InputValidationError
from ...models import CalculationRecord
from ...persistence import write_autosave
from ..widgets import CrossSectionWidget,HelpPanel
class ReviewPage(QWizardPage):
    def __init__(self):
        super().__init__(); self.setTitle("Review geometry"); layout=QVBoxLayout(self); self.error=QLabel(); self.error.setStyleSheet("color:#b00020;font-weight:bold"); self.diagram=CrossSectionWidget(); self.checklist=QLabel(); self.checklist.setWordWrap(True); layout.addWidget(self.error); layout.addWidget(self.diagram); layout.addWidget(self.checklist); layout.addWidget(HelpPanel("Check the entire section from left to right. Dark grey is an internal vehicle area; yellow is painted separation included in Wk; blue is external sealed allowance; the red line is final Wk.")); self._valid=False
    def initializePage(self):
        try:
            road=self.wizard().build_road(); result=calculate_wk(road); self.wizard().road_input=road; self.wizard().result=result; write_autosave(CalculationRecord(road_input=road,result=result)); self.error.clear(); self.diagram.set_calculation(road,result); checks=[]
            kinds={s.segment_type for s in road.segments}
            if SegmentType.TURN_LANE in kinds:checks.append("✓ Turn lane included")
            if SegmentType.INTERNAL_PAINTED_SEPARATION in kinds:checks.append("✓ Painted internal separation included")
            if not road.full_kerb_to_kerb_is_travelled:checks.append("✓ Outer traffic-edge lines selected")
            if any(s and s.surface_beyond_edge==SurfaceType.UNSEALED for s in (road.left_boundary,road.right_boundary)):checks.append("✓ Unsealed area excluded")
            if road.physical_median_present:checks.append("✓ Physical median handled as a divided carriageway")
            self.checklist.setText("\n".join(checks)); self._valid=True
        except (ValueError,InputValidationError) as error:self.error.setText(str(error)); self._valid=False
        self.completeChanged.emit()
    def isComplete(self):return self._valid
