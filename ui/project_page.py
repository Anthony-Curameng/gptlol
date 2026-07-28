from PySide6.QtWidgets import QFormLayout, QLineEdit, QWizardPage
from wkcalc.models import ProjectDetails

class ProjectPage(QWizardPage):
    def __init__(self):
        super().__init__(); self.setTitle("Project details"); self.setSubTitle("Optional identifiers stored with the calculation.")
        form = QFormLayout(self); self.inputs = {}
        for key, label in (("project", "Project"), ("road_name", "Road name"), ("section", "Section or chainage"), ("road_authority", "Road authority"), ("calculation_reference", "Calculation reference")):
            self.inputs[key] = QLineEdit(); form.addRow(label, self.inputs[key])
    def validatePage(self):
        self.wizard().project = ProjectDetails(**{key: field.text().strip() for key, field in self.inputs.items()}); return True

    def load_details(self, details: ProjectDetails):
        for key, field in self.inputs.items(): field.setText(getattr(details, key))
