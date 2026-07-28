import pytest
pytest.importorskip("PySide6")
from wkcalc.ui import CalculatorWizard

def test_wizard_has_seven_pages_and_starts_incomplete(qtbot):
    wizard=CalculatorWizard();qtbot.addWidget(wizard);assert len(wizard.pageIds())==7;assert not wizard.currentPage().isComplete()

def test_full_kerb_mode_skips_boundary_pages(qtbot):
    wizard=CalculatorWizard();qtbot.addWidget(wizard);wizard.cross_section_page.full.setChecked(True);wizard.setStartId(wizard.CROSS_SECTION);wizard.restart();assert wizard.nextId()==wizard.AUTHORITY
