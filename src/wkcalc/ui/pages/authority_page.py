from PySide6.QtWidgets import QComboBox,QDoubleSpinBox,QFormLayout,QLineEdit,QVBoxLayout,QWizardPage
from ...enums import AuthorityRule
from ..widgets import HelpPanel
class AuthorityPage(QWizardPage):
    def __init__(self):
        super().__init__(); self.setTitle("Authority direction"); self.rule=QComboBox(); self.rule.addItem("No authority adjustment",AuthorityRule.NONE); self.rule.addItem("Authority-specified final Wk",AuthorityRule.FINAL_OVERRIDE); self.rule.addItem("Authority-specified minimum Wk",AuthorityRule.MINIMUM); self.name=QLineEdit(); self.reference=QLineEdit(); self.width=QDoubleSpinBox(); self.width.setRange(0,100); self.width.setDecimals(2); self.width.setSpecialValueText("Required"); self.width.setSuffix(" m"); layout=QVBoxLayout(self); self.form=QFormLayout(); self.form.addRow("Mode",self.rule); self.form.addRow("Authority name",self.name); self.form.addRow("Reference or document note",self.reference); self.form.addRow("Authority width",self.width); layout.addLayout(self.form); layout.addWidget(HelpPanel("Authority adjustment is disabled by default. Enabling it requires the authority, its document reference and the directed width. A value beyond sealed geometry blocks calculation.")); self.rule.currentIndexChanged.connect(self._mode); self.name.textChanged.connect(self.completeChanged); self.reference.textChanged.connect(self.completeChanged); self.width.valueChanged.connect(self.completeChanged); self._mode()
    def _mode(self):
        enabled=self.rule.currentData()!=AuthorityRule.NONE
        for field in (self.name,self.reference,self.width):field.setVisible(enabled); self.form.labelForField(field).setVisible(enabled)
        self.completeChanged.emit()
    def isComplete(self):return self.rule.currentData()==AuthorityRule.NONE or bool(self.name.text().strip() and self.reference.text().strip() and self.width.value()>0)
