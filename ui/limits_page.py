from PySide6.QtWidgets import QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QMessageBox, QWizardPage
from wkcalc.enums import AuthorityRule
from wkcalc.models import RoadInput
from wkcalc.validation import GeometryError, validate_road

class LimitsPage(QWizardPage):
    def __init__(self):
        super().__init__(); self.setTitle("Limiting dimensions"); self.setSubTitle("Enable only dimensions that apply to this cross-section.")
        form=QFormLayout(self); self.use_kerb=QCheckBox("Apply"); self.kerb=self._spin(14.2); self.use_sealed=QCheckBox("Apply"); self.sealed=self._spin(16); self.max_side=self._spin(3); self.max_side.setMaximum(3)
        self.authority_rule=QComboBox(); self.authority_rule.addItem("None",AuthorityRule.NONE); self.authority_rule.addItem("Minimum",AuthorityRule.MINIMUM); self.authority_rule.addItem("Override",AuthorityRule.OVERRIDE); self.authority=self._spin(12)
        form.addRow("Kerb-to-kerb limit",self.use_kerb); form.addRow("Kerb-to-kerb width",self.kerb); form.addRow("Total sealed-width limit",self.use_sealed); form.addRow("Total sealed width",self.sealed); form.addRow("Maximum side allowance",self.max_side); form.addRow("Authority rule",self.authority_rule); form.addRow("Authority width",self.authority)
        self.use_kerb.toggled.connect(self.kerb.setEnabled); self.use_sealed.toggled.connect(self.sealed.setEnabled); self.authority_rule.currentIndexChanged.connect(lambda: self.authority.setEnabled(self.authority_rule.currentData()!=AuthorityRule.NONE)); self.kerb.setEnabled(False); self.sealed.setEnabled(False); self.authority.setEnabled(False)
    def _spin(self,value):
        field=QDoubleSpinBox(); field.setRange(.01,1000); field.setDecimals(2); field.setValue(value); field.setSuffix(" m"); return field
    def build_road(self):
        rule=self.authority_rule.currentData()
        return RoadInput(travelled_width_m=self.wizard().travelled_width_m,left=self.wizard().left,right=self.wizard().right,kerb_to_kerb_width_m=self.kerb.value() if self.use_kerb.isChecked() else None,total_sealed_width_m=self.sealed.value() if self.use_sealed.isChecked() else None,authority_width_m=self.authority.value() if rule!=AuthorityRule.NONE else None,authority_rule=rule,maximum_side_allowance_m=self.max_side.value())
    def validatePage(self):
        try: self.wizard().road=self.build_road(); validate_road(self.wizard().road)
        except (GeometryError,ValueError) as error: QMessageBox.warning(self,"Invalid geometry",str(error)); return False
        return True

    def load_road(self, road):
        self.use_kerb.setChecked(road.kerb_to_kerb_width_m is not None)
        if road.kerb_to_kerb_width_m is not None: self.kerb.setValue(road.kerb_to_kerb_width_m)
        self.use_sealed.setChecked(road.total_sealed_width_m is not None)
        if road.total_sealed_width_m is not None: self.sealed.setValue(road.total_sealed_width_m)
        self.max_side.setValue(road.maximum_side_allowance_m); self.authority_rule.setCurrentIndex(self.authority_rule.findData(road.authority_rule))
        if road.authority_width_m is not None: self.authority.setValue(road.authority_width_m)
