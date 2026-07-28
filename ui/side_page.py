from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QFormLayout, QLabel, QStackedWidget, QWizardPage, QWidget
from wkcalc.enums import BOUNDARY_LABELS, BoundaryType, SurfaceType
from wkcalc.models import SideInput

class SidePage(QWizardPage):
    def __init__(self, side: str):
        super().__init__(); self.side=side; self.setTitle(f"{side.title()}-side boundary"); self.setSubTitle("This side is evaluated independently.")
        form=QFormLayout(self); self.boundary=QComboBox()
        for value,label in BOUNDARY_LABELS.items(): self.boundary.addItem(label,value)
        self.distance=self._spin(); self.width=self._spin(); self.authority=self._spin(); self.surface=QComboBox(); self.surface.addItem("Sealed",SurfaceType.SEALED); self.surface.addItem("Unsealed",SurfaceType.UNSEALED)
        form.addRow("Boundary type",self.boundary); form.addRow("Distance to kerb",self.distance); form.addRow("Surface to kerb",self.surface); form.addRow("Width beyond edge line",self.width); form.addRow("Authority side allowance",self.authority)
        self.boundary.currentIndexChanged.connect(self._conditional); self._conditional()
    def _spin(self):
        field=QDoubleSpinBox(); field.setRange(0,100); field.setDecimals(2); field.setSuffix(" m"); return field
    def _conditional(self):
        boundary=self.boundary.currentData(); kerb=boundary==BoundaryType.KERB_BEYOND_EDGE_LINE; beyond=boundary in {BoundaryType.SEALED_BEYOND_EDGE_LINE,BoundaryType.UNSEALED_BEYOND_EDGE_LINE}; authority=boundary==BoundaryType.AUTHORITY_DEFINED
        for field, visible in ((self.distance, kerb), (self.surface, kerb), (self.width, beyond), (self.authority, authority)):
            field.setVisible(visible); self.layout().labelForField(field).setVisible(visible)
    def validatePage(self):
        boundary=self.boundary.currentData(); values={"boundary_type":boundary}
        if boundary==BoundaryType.KERB_BEYOND_EDGE_LINE: values.update(distance_to_kerb_m=self.distance.value(),surface=self.surface.currentData())
        elif boundary in {BoundaryType.SEALED_BEYOND_EDGE_LINE,BoundaryType.UNSEALED_BEYOND_EDGE_LINE}: values["width_beyond_edge_m"]=self.width.value()
        elif boundary==BoundaryType.AUTHORITY_DEFINED: values["authority_allowance_m"]=self.authority.value()
        setattr(self.wizard(),self.side,SideInput(**values)); return True

    def load_side(self, side):
        index=self.boundary.findData(side.boundary_type); self.boundary.setCurrentIndex(index)
        if side.distance_to_kerb_m is not None: self.distance.setValue(side.distance_to_kerb_m)
        if side.width_beyond_edge_m is not None: self.width.setValue(side.width_beyond_edge_m)
        if side.authority_allowance_m is not None: self.authority.setValue(side.authority_allowance_m)
        if side.surface is not None: self.surface.setCurrentIndex(self.surface.findData(side.surface))
