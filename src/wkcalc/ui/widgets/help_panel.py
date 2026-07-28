from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout
class HelpPanel(QGroupBox):
    def __init__(self,text,parent=None):
        super().__init__("What does this mean?",parent); label=QLabel(text); label.setWordWrap(True); layout=QVBoxLayout(self); layout.addWidget(label)
