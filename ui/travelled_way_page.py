from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDoubleSpinBox, QHBoxLayout, QHeaderView, QLabel, QPushButton, QRadioButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWizardPage
from wkcalc.calculator import calculate_travelled_width
from wkcalc.models import TravelledElement

class TravelledWayPage(QWizardPage):
    DEFAULTS = [("Through lane", 2, 3.5, True), ("Turn lane", 1, 3.0, True), ("Bicycle lane", 1, 1.5, True), ("Parking lane", 1, 2.3, False), ("Other travelled area", 1, 1.0, False)]
    def __init__(self):
        super().__init__(); self.setTitle("Travelled-way composition"); self.setSubTitle("Enter a direct width or sum included travelled areas.")
        layout = QVBoxLayout(self); self.direct = QRadioButton("Direct width"); self.elements_mode = QRadioButton("Element-based"); self.direct.setChecked(True)
        self.width = QDoubleSpinBox(); self.width.setRange(.01, 1000); self.width.setDecimals(2); self.width.setValue(10.5); self.width.setSuffix(" m")
        self.table = QTableWidget(len(self.DEFAULTS), 5); self.table.setHorizontalHeaderLabels(["Type", "Quantity", "Individual width (m)", "Included", "Notes"]); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for row, (name, qty, width, included) in enumerate(self.DEFAULTS):
            for column, value in enumerate((name, qty, width, "Yes" if included else "No", "")): self.table.setItem(row, column, QTableWidgetItem(str(value)))
        self.total = QLabel(); controls = QHBoxLayout(); add = QPushButton("Add lane / area"); remove = QPushButton("Remove selected row"); controls.addWidget(add); controls.addWidget(remove); controls.addStretch()
        layout.addWidget(self.direct); layout.addWidget(self.width); layout.addWidget(self.elements_mode); layout.addWidget(self.table); layout.addLayout(controls); layout.addWidget(self.total)
        add.clicked.connect(self._add_row); remove.clicked.connect(self._remove_row)
        self.direct.toggled.connect(self._mode); self.table.itemChanged.connect(self._update_total); self._mode(); self._update_total()
    def _mode(self):
        self.width.setEnabled(self.direct.isChecked()); self.table.setEnabled(not self.direct.isChecked())
    def _elements(self):
        values=[]
        for row in range(self.table.rowCount()):
            try:
                values.append(TravelledElement(element_type=self.table.item(row,0).text(), quantity=int(self.table.item(row,1).text()), individual_width=float(self.table.item(row,2).text()), included=self.table.item(row,3).text().strip().lower() in {"yes","true","1","y"}, notes=self.table.item(row,4).text()))
            except (ValueError, AttributeError): continue
        return values
    def _update_total(self): self.total.setText(f"Included travelled width: {calculate_travelled_width(self._elements()):.2f} m")
    def _add_row(self):
        row = self.table.rowCount(); self.table.insertRow(row)
        for column, value in enumerate(("Lane", 1, 3.5, "Yes", "")): self.table.setItem(row, column, QTableWidgetItem(str(value)))
        self.table.setCurrentCell(row, 0); self.table.editItem(self.table.item(row, 0))
    def _remove_row(self):
        if self.table.currentRow() >= 0: self.table.removeRow(self.table.currentRow()); self._update_total()
    def validatePage(self):
        if self.direct.isChecked(): self.wizard().travelled_width_m, self.wizard().elements = self.width.value(), []
        else:
            self.wizard().elements = self._elements(); self.wizard().travelled_width_m = calculate_travelled_width(self.wizard().elements)
            if self.wizard().travelled_width_m <= 0: return False
        return True

    def load_composition(self, width_m, elements):
        self.width.setValue(width_m)
        if not elements:
            self.direct.setChecked(True); return
        self.elements_mode.setChecked(True); self.table.setRowCount(len(elements))
        for row, element in enumerate(elements):
            values=(element.element_type,element.quantity,element.individual_width,"Yes" if element.included else "No",element.notes)
            for column,value in enumerate(values): self.table.setItem(row,column,QTableWidgetItem(str(value)))
        self._update_total()
