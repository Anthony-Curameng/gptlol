from PySide6.QtWidgets import QCheckBox,QDoubleSpinBox,QRadioButton,QVBoxLayout,QWizardPage
from ...enums import WidthInputMode
from ..widgets import HelpPanel,SegmentEditor
class CrossSectionPage(QWizardPage):
    def __init__(self):
        super().__init__(); self.setTitle("Internal cross-section"); layout=QVBoxLayout(self)
        self.full=QCheckBox("The complete sealed kerb-to-kerb width is travelled"); self.simple=QRadioButton("Simple outer-edge-to-outer-edge width"); self.detailed=QRadioButton("Detailed ordered segments, left to right"); self.simple.setChecked(True)
        self.width=QDoubleSpinBox(); self.width.setRange(0,100); self.width.setDecimals(2); self.width.setSpecialValueText("Required"); self.width.setSuffix(" m")
        self.editor=SegmentEditor(); self.verify_total=QCheckBox("Supply kerb-to-kerb total as a geometry verification value"); self.total=QDoubleSpinBox(); self.total.setRange(0,100); self.total.setDecimals(2); self.total.setSpecialValueText("Required"); self.total.setSuffix(" m")
        for widget in (self.full,self.simple,self.width,self.detailed,self.editor,self.verify_total,self.total):layout.addWidget(widget)
        layout.addWidget(HelpPanel("The internal span runs between the two outer traffic edges. Internal painted separation — included within Wk. A physical median must not be added here."))
        self.full.toggled.connect(self._mode); self.simple.toggled.connect(self._mode); self.verify_total.toggled.connect(self._mode); self.width.valueChanged.connect(self.completeChanged); self.total.valueChanged.connect(self.completeChanged); self.editor.changed.connect(self.completeChanged); self._mode()
    def _mode(self):
        self.simple.setEnabled(not self.full.isChecked()); self.detailed.setEnabled(not self.full.isChecked()); self.editor.setVisible(not self.full.isChecked() and self.detailed.isChecked()); self.width.setVisible(self.full.isChecked() or self.simple.isChecked()); self.verify_total.setVisible(not self.full.isChecked()); self.total.setVisible(not self.full.isChecked() and self.verify_total.isChecked()); self.completeChanged.emit()
    def isComplete(self):
        internal_ok=self.width.value()>0 if self.full.isChecked() or self.simple.isChecked() else self.editor.is_valid()
        return internal_ok and (not self.verify_total.isChecked() or self.total.value()>0)
    def width_mode(self):return WidthInputMode.SIMPLE if self.simple.isChecked() or self.full.isChecked() else WidthInputMode.DETAILED
