from PySide6.QtWidgets import QPushButton
from .left_boundary_page import BoundaryPage
class RightBoundaryPage(BoundaryPage):
    def __init__(self):
        super().__init__("right"); button=QPushButton("Copy left-side settings"); self.layout().insertWidget(0,button); button.clicked.connect(lambda:self.copy_from(self.wizard().left_boundary_page))
