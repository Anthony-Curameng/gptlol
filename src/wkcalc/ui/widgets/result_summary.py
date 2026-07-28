from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel
class ResultSummary(QGroupBox):
    def __init__(self,parent=None): super().__init__("Calculation",parent); self.form=QFormLayout(self)
    def set_result(self,result):
        while self.form.rowCount():self.form.removeRow(0)
        rows=(("Internal span",result.internal_width_m),("Left allowance",result.left_allowance_m),("Right allowance",result.right_allowance_m),("Unrestricted Wk",result.unrestricted_wk_m),("Physical Wk",result.physical_wk_m),("Final Wk",result.final_wk_m))
        for label,value in rows:self.form.addRow(label,QLabel(f"<b>{value:.2f} m</b>" if label=="Final Wk" else f"{value:.2f} m"))
