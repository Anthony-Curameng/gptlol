from PySide6.QtCore import Signal
from PySide6.QtWidgets import QAbstractItemView, QComboBox, QDoubleSpinBox, QHeaderView, QHBoxLayout, QLabel, QPushButton, QSpinBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from ...constants import PAINTED_SEPARATION_HELP
from ...enums import SegmentType
from ...models import CrossSectionSegment

LABELS={SegmentType.THROUGH_LANE:"Through lane",SegmentType.TURN_LANE:"Turn lane",SegmentType.PARKING_LANE:"Parking lane",SegmentType.BICYCLE_LANE:"Bicycle lane",SegmentType.INTERNAL_PAINTED_SEPARATION:"Internal painted separation",SegmentType.OTHER_INTERNAL_SEALED:"Other internal sealed area"}
class SegmentEditor(QWidget):
    changed=Signal()
    TEMPLATES={"Two-way road":[(SegmentType.THROUGH_LANE,"Direction 1"),(SegmentType.THROUGH_LANE,"Direction 2")],"Two-way road with centre turn lane":[(SegmentType.THROUGH_LANE,"Direction 1"),(SegmentType.TURN_LANE,"Centre turn lane"),(SegmentType.THROUGH_LANE,"Direction 2")],"Two-way road with painted median":[(SegmentType.THROUGH_LANE,"Direction 1"),(SegmentType.INTERNAL_PAINTED_SEPARATION,"Painted median"),(SegmentType.THROUGH_LANE,"Direction 2")],"One-way carriageway":[(SegmentType.THROUGH_LANE,"Lane 1")],"Custom":[]}
    def __init__(self,parent=None):
        super().__init__(parent); layout=QVBoxLayout(self); top=QHBoxLayout(); self.template=QComboBox(); self.template.addItem("Select a template…",None)
        for name in self.TEMPLATES:self.template.addItem(name,name)
        add=QPushButton("Add segment"); top.addWidget(QLabel("Template")); top.addWidget(self.template); top.addWidget(add); top.addStretch(); layout.addLayout(top)
        self.table=QTableWidget(0,6); self.table.setHorizontalHeaderLabels(["Type","Label","Quantity","Individual width","Total width","Actions"]); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows); layout.addWidget(self.table)
        self.notice=QLabel(); self.notice.setWordWrap(True); self.subtotal=QLabel("Internal subtotal: 0.00 m"); layout.addWidget(self.notice); layout.addWidget(self.subtotal)
        add.clicked.connect(lambda:self.add_segment(SegmentType.THROUGH_LANE,"New segment")); self.template.currentIndexChanged.connect(self._template); self.table.itemChanged.connect(self._update)
    def _template(self):
        name=self.template.currentData()
        if name is None:return
        self.table.setRowCount(0)
        for kind,label in self.TEMPLATES[name]: self.add_segment(kind,label)
        self.notice.setText("Template dimensions are blank and require confirmation."); self.template.setCurrentIndex(0); self.changed.emit()
    def add_segment(self,kind,label,width=0.0,quantity=1):
        row=self.table.rowCount(); self.table.insertRow(row); combo=QComboBox()
        for value,text in LABELS.items():combo.addItem(text,value)
        combo.setCurrentIndex(combo.findData(kind)); combo.currentIndexChanged.connect(self._update); self.table.setCellWidget(row,0,combo); self.table.setItem(row,1,QTableWidgetItem(label))
        qty=QSpinBox(); qty.setRange(1,20); qty.setValue(quantity); qty.valueChanged.connect(self._update); self.table.setCellWidget(row,2,qty)
        size=QDoubleSpinBox(); size.setRange(0,100); size.setDecimals(2); size.setSpecialValueText("Required"); size.setSuffix(" m"); size.setValue(width); size.valueChanged.connect(self._update); self.table.setCellWidget(row,3,size); self.table.setItem(row,4,QTableWidgetItem("0.00 m"))
        actions=QWidget(); buttons=QHBoxLayout(actions); buttons.setContentsMargins(0,0,0,0)
        for text,fn in (("←",lambda:self._move(actions,-1)),("→",lambda:self._move(actions,1)),("Duplicate",lambda:self._duplicate(actions)),("Delete",lambda:self._delete(actions))): button=QPushButton(text); button.clicked.connect(fn); buttons.addWidget(button)
        self.table.setCellWidget(row,5,actions); self._update()
    def _row(self,widget):
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row,5) is widget:return row
        return -1
    def _snapshot(self,row): return (self.table.cellWidget(row,0).currentData(),self.table.item(row,1).text(),self.table.cellWidget(row,3).value(),self.table.cellWidget(row,2).value())
    def _move(self,widget,delta):
        row=self._row(widget); target=row+delta
        if row<0 or not 0<=target<self.table.rowCount():return
        rows=[self._snapshot(i) for i in range(self.table.rowCount())]; rows[row],rows[target]=rows[target],rows[row]; self.table.setRowCount(0)
        for values in rows:self.add_segment(*values)
    def _duplicate(self,widget):
        row=self._row(widget)
        if row>=0:self.add_segment(*self._snapshot(row))
    def _delete(self,widget):
        row=self._row(widget)
        if row>=0:self.table.removeRow(row); self._update()
    def _update(self,*_):
        total=0; painted=False
        for row in range(self.table.rowCount()):
            value=self.table.cellWidget(row,2).value()*self.table.cellWidget(row,3).value(); self.table.item(row,4).setText(f"{value:.2f} m"); total+=value; painted |= self.table.cellWidget(row,0).currentData()==SegmentType.INTERNAL_PAINTED_SEPARATION
        self.subtotal.setText(f"Internal subtotal: {total:.2f} m"); self.notice.setText(PAINTED_SEPARATION_HELP if painted else self.notice.text()); self.changed.emit()
    def segments(self):
        return tuple(CrossSectionSegment(segment_type=self.table.cellWidget(r,0).currentData(),label=self.table.item(r,1).text().strip(),quantity=self.table.cellWidget(r,2).value(),width_m=self.table.cellWidget(r,3).value()) for r in range(self.table.rowCount()))
    def is_valid(self): return self.table.rowCount()>0 and all(self.table.cellWidget(r,3).value()>0 and self.table.item(r,1).text().strip() for r in range(self.table.rowCount()))
